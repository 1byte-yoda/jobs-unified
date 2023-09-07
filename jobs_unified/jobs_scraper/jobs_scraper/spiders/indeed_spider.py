import datetime
import json
import logging
import re
import socket

import scrapy
from itemloaders.processors import TakeFirst
from scrapy.loader import ItemLoader
from scrapy.http.response.html import HtmlResponse
from scrapy_selenium import SeleniumRequest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from chromedriver_py import binary_path

from jobs_scraper.items import IndeedItem

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

        loader = ItemLoader(item=IndeedItem())
        loader.default_output_processor = TakeFirst()

        loader.add_value("base_url", json_response.get("baseUrl"))
        loader.add_value("benefits_model", json_response.get("benefitsModel"))
        loader.add_value("categorized_attribute_model", json_response.get("categorizedAttributeModel"))
        loader.add_value("cmi_job_category_model", json_response.get("cmiJobCategoryModel"))
        loader.add_value("commute_info_model", json_response.get("commuteInfoModel"))
        loader.add_value("company_avatar_model", json_response.get("companyAvatarModel"))
        loader.add_value("company_follow_form_model", json_response.get("companyFollowFormModel"))
        loader.add_value("company_tab_model", json_response.get("companyTabModel"))
        loader.add_value("contact_person_model", json_response.get("contactPersonModel"))
        loader.add_value("country", json_response.get("country"))
        loader.add_value("indeed_apply_button_container", json_response.get("indeedApplyButtonContainer"))
        loader.add_value("job_info_wrapper_model", json_response.get("jobInfoWrapperModel"))
        loader.add_value("job_key", json_response.get("jobKey"))
        loader.add_value("job_location", json_response.get("jobLocation"))
        loader.add_value("job_metadata_footer_model", json_response.get("jobMetadataFooterModel"))
        loader.add_value("job_title", json_response.get("jobTitle"))
        loader.add_value("language", json_response.get("language"))
        loader.add_value("last_visit_time", json_response.get("lastVisitTime"))
        loader.add_value("lazy_providers", json_response.get("lazyProviders"))
        loader.add_value("locale", json_response.get("locale"))
        loader.add_value("request_path", json_response.get("requestPath"))
        loader.add_value("salary_info_model", json_response.get("salaryInfoModel"))

        loader.add_value(field_name="url", value=response.url)
        loader.add_value(field_name="project", value=self.settings.get("BOT_NAME"))
        loader.add_value(field_name="spider", value=self.name)
        loader.add_value(field_name="server", value=socket.gethostname())
        loader.add_value(field_name="date", value=datetime.datetime.now().isoformat())

        yield loader.load_item()
