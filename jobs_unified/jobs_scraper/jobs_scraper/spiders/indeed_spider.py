import json
import logging
import re

import scrapy
from scrapy.http.response.html import HtmlResponse
from scrapy_selenium import SeleniumRequest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from chromedriver_py import binary_path


logging.getLogger("selenium.webdriver.remote.remote_connection").setLevel("INFO")


class IndeedSpider(scrapy.Spider):
    URL = "https://ph.indeed.com/jobs?q=all&pp=gQAAAAAAAAAAAAAAAAACD-M2ugADAAABAAA"
    name = "indeed"

    @staticmethod
    def get_html_page(url):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36')
        driver = webdriver.Chrome(options=chrome_options, executable_path=binary_path)
        driver.get(url)

        return driver.page_source

    @classmethod
    def get_total_pages(cls) -> int:
        jobs_per_pages = 15
        html_body = cls.get_html_page(url=cls.URL)
        response = HtmlResponse(url=cls.URL, body=html_body, encoding="utf-8")
        total_jobs = response.xpath("//div[contains(@class, 'jobCount')]//span//text()").extract_first()
        total_jobs = int(total_jobs.strip(" jobs").replace(",", ""))
        return 1 + (total_jobs // jobs_per_pages)

    def start_requests(self):
        total_pages = self.get_total_pages()

        urls = [f"{self.URL}&start={i}" for i in range(0, total_pages + 10, 10)]
        for url in [urls[0]]:
            yield SeleniumRequest(url=url, callback=self.parse)

    def parse(self, response: HtmlResponse, **kwargs):
        job_links = response.xpath("//a[contains(@class, 'jcs-JobTitle') and contains(@id, 'job_')]/@href").extract()
        indeed_view_job_url = "https://ph.indeed.com"

        for url_path in [job_links[0]]:
            req_url = f"{indeed_view_job_url}{url_path}"

            yield SeleniumRequest(url=req_url, callback=self.parse_job_card)

    def parse_job_card(self, response: HtmlResponse):
        data = re.findall(r'window._initialData=(\{.+?\});', response.text)
        json_response = json.loads(data[0])
        print(json_response)
