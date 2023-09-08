import datetime
import json
import logging
import re
import socket

import requests
import scrapy
from itemloaders.processors import TakeFirst
from scrapy.loader import ItemLoader
from scrapy.http.response.html import HtmlResponse
from scrapy.http.request.json_request import JsonRequest

from jobs_scraper.items import IndeedItem

logger = logging.getLogger("scrapy.core.scraper")


class IndeedFlareSpider(scrapy.Spider):
    URL = "https://ph.indeed.com/jobs?filter=0&q=all&l=Philippines&sort=date"
    name = "indeed_flare"

    flare_base_url = "http://localhost:8191/v1"
    flare_headers = {'Content-Type': 'application/json'}

    @classmethod
    def get_total_pages(cls):
        post_body = {'cmd': 'request.get', 'url': cls.URL, 'maxTimeout': 60000}
        response = requests.post(cls.flare_base_url, headers=cls.flare_headers, json=post_body)
        html_response = HtmlResponse(url=cls.URL, body=response.json()["solution"]["response"], encoding="utf-8")
        total_jobs = html_response.xpath("//*[contains(@class, 'jobCount')]/span/text()").extract_first()

        jobs_per_page = 15
        margin_offset = 10
        total_pages = margin_offset + (int(total_jobs.split(" ")[0].replace(",", "")) // jobs_per_page)

        logger.debug(f"There are {total_jobs} jobs to be scraped within {total_pages} pages")

        return total_pages

    def start_requests(self):

        urls = [f"{self.URL}&start={i}" for i in range(0, self.get_total_pages(), 10)]

        for url in urls:
            post_body = {'cmd': 'request.get', 'url': url, 'maxTimeout': 60000}
            yield JsonRequest(url=self.flare_base_url, headers=self.flare_headers, data=post_body, callback=self.parse)

    def parse(self, response: HtmlResponse, **kwargs):
        json_response = response.json()

        logger.debug(f"Scraped from <{json_response['solution']['status']}{json_response['solution']['url']}>")

        response = HtmlResponse(url=json_response["solution"]["url"], body=json_response["solution"]["response"], encoding="utf-8")

        job_keys = response.xpath("//a[contains(@class, 'jcs-JobTitle')]/@id").extract()
        indeed_view_job_url = "https://ph.indeed.com/viewjob?jk="

        for jk in job_keys:
            sanitized_jk = jk.split("_")[-1]
            post_body = {'cmd': 'request.get', 'url': f"{indeed_view_job_url}{sanitized_jk}", 'maxTimeout': 60000}
            yield JsonRequest(url=self.flare_base_url, headers=self.flare_headers, data=post_body, callback=self.parse_job_card)

    def parse_job_card(self, response: HtmlResponse):
        json_response = response.json()

        logger.debug(f"Scraped from <{json_response['solution']['status']}{json_response['solution']['url']}>")

        response = HtmlResponse(url=json_response["solution"]["url"], body=json_response["solution"]["response"], encoding="utf-8")
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

        else:
            logger.warning(r"HTML Response might have changed, 'window._initialData=(\{.+?\}' didn't matched a JSON data")

        loader.add_value(field_name="url", value=response.url)
        loader.add_value(field_name="project", value=self.settings.get("BOT_NAME"))
        loader.add_value(field_name="spider", value=self.name)
        loader.add_value(field_name="server", value=socket.gethostname())
        loader.add_value(field_name="date", value=datetime.datetime.now().isoformat())

        yield loader.load_item()
