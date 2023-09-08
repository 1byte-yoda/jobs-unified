import datetime
import json
import logging
import random
import re
import socket
import scrapy
from itemloaders.processors import TakeFirst
from scrapy.loader import ItemLoader
from scrapy.http.response.html import HtmlResponse
from scrapy_selenium import SeleniumRequest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from chromedriver_py import binary_path

from jobs_scraper.items import IndeedItem

logging.getLogger("selenium.webdriver.remote.remote_connection").setLevel("INFO")


class IndeedSpider(scrapy.Spider):
    URL = "https://ph.indeed.com/jobs?filter=0&q=all&l=Philippines&pp=gQAAAAAAAAAAAAAAAAACD-M2ugADAAABAAA"
    name = "indeed"

    def start_requests(self):

        urls = [f"{self.URL}&start={i}" for i in range(0, 700, 10)]
        for url in urls:
            yield SeleniumRequest(url=url, callback=self.parse, wait_time=random.randint(1, 4))

    def parse(self, response: HtmlResponse, **kwargs):
        job_links = response.xpath("//a[contains(@class, 'jcs-JobTitle') and contains(@id, 'job_')]/@href").extract()
        indeed_view_job_url = "https://ph.indeed.com/viewjob?jk="

        for url_path in job_links:
            if url_path.startswith("/rc/"):
                jk = re.findall(r"jk=(.+)&.+", url_path)[0].split("&")[0]
            else:
                jk = url_path.split("?")[0].split("-")[-1]

            yield SeleniumRequest(url=f"{indeed_view_job_url}{jk}", callback=self.parse_job_card, wait_time=random.randint(1, 4))

    def parse_job_card(self, response: HtmlResponse):
        data = re.findall(r'window._initialData=(\{.+?\});', response.text)
        # data = re.findall(r'(\{"accountKey".+"jobInfoWrapperModel".*\});', response.text)

        loader = ItemLoader(item=IndeedItem())
        loader.default_output_processor = TakeFirst()

        if len(data) > 0:
            json_response = json.loads(data[0])
            loader.add_value("base_url", json_response.get("baseUrl"))
            loader.add_value("benefits_model", json.dumps(json_response.get("benefitsModel", {})))
            loader.add_value("country", json_response.get("country"))
            loader.add_value("hiring_insights_model", json.dumps(json_response.get("hiringInsightsModel", {})))
            loader.add_value("job_info_wrapper_model", json.dumps(json_response.get("jobInfoWrapperModel", {})))
            loader.add_value("job_key", json_response.get("jobKey"))
            loader.add_value("job_location", json_response.get("jobLocation"))
            loader.add_value("job_metadata_footer_model", json_response.get("jobMetadataFooterModel"))
            loader.add_value("job_title", json_response.get("jobTitle"))
            loader.add_value("language", json_response.get("language"))
            loader.add_value("locale", json_response.get("locale"))
            loader.add_value("request_path", json_response.get("requestPath"))
            loader.add_value("salary_info_model", json.dumps(json_response.get("salaryInfoModel", {})))

        loader.add_value(field_name="url", value=response.url)
        loader.add_value(field_name="project", value=self.settings.get("BOT_NAME"))
        loader.add_value(field_name="spider", value=self.name)
        loader.add_value(field_name="server", value=socket.gethostname())
        loader.add_value(field_name="date", value=datetime.datetime.now().isoformat())

        yield loader.load_item()
