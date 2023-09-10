import datetime
import json
import logging
import math
import socket

import requests
import scrapy
from scrapy.http.response.html import HtmlResponse
from scrapy.selector import Selector
from itemloaders import ItemLoader
from itemloaders.processors import TakeFirst

from jobs_scraper.items import FoundItItem

logger = logging.getLogger("scrapy.core.scraper")


class FoundItSpider(scrapy.Spider):
    job_url = "https://www.foundit.com.ph/middleware/jobsearch?sort=1&limit=100&query=&locations=Philippines&queryDerived=true"
    job_details_url = "https://www.foundit.com.ph/middleware/jobdetail/"
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
        "Referer": "http://www.foundit.com.ph/",
    }
    offset = 100
    custom_settings = {
        'CONCURRENT_REQUESTS': 32,
        'DOWNLOAD_DELAY': 0.5
    }
    name = "foundit"

    @classmethod
    def get_total_pages(cls):
        response = requests.get(url=f"{cls.job_url}&start=0", headers=cls.headers)

        if response.status_code >= 400:
            return 0

        response_json = response.json()
        total_jobs = response_json.get("jobSearchResponse", {}).get("meta", {}).get("paging", {}).get("total", 0)
        return int(math.ceil(total_jobs / cls.offset))

    def start_requests(self):
        total_pages = self.get_total_pages()
        logger.info(f"Starting scraper with {total_pages} pages...")
        for i in range(0, total_pages + self.offset):
            url = f"{self.job_url}&start={i * self.offset}"
            logger.info(f"Working on page {i * self.offset}")
            yield scrapy.Request(url=url, headers=self.headers, callback=self.parse)

    def parse(self, response: HtmlResponse, **kwargs):
        response_json = response.json()

        if response_json.get("jobSearchStatus") == 200:
            jobs = response_json["jobSearchResponse"].get("data", [])

            logger.info(f"Scraping {len(jobs)} jobs...")

            for job in jobs:
                if "id" in job or "jobId" in job:
                    job_url = f"{self.job_details_url}{job['jobId']}"
                    logger.info(f"Scraping Job {job['id']} - {job['title']}")
                    yield scrapy.Request(url=job_url, headers=self.headers, callback=self.parse_job_item, cb_kwargs={"job": job})
                else:
                    logger.warning(f"Invalid Job JSON: {job}")

    def parse_job_item(self, response: HtmlResponse, job: dict):
        selector = Selector(response=response, type="html")
        loader = ItemLoader(item=FoundItItem(), selector=selector)
        loader.default_output_processor = TakeFirst()
        json_response = response.json()

        # Company
        loader.add_value(field_name="company_name", value=job.get("companyName"))
        loader.add_value(field_name="company_url", value=job.get("seoCompanyUrl"))

        # Job
        loader.add_value(field_name="job_id", value=job.get("jobId"))
        loader.add_value(field_name="job_title", value=job.get("title"))
        loader.add_value(field_name="job_exp", value=job.get("exp"))
        loader.add_value(field_name="job_description", value=json_response.get("jobDetailResponse", {}).get("description"))
        loader.add_value(field_name="employment_types", value=json.dumps(job.get("employmentTypes", [])))
        loader.add_value(field_name="locations", value=job.get("locations"))
        loader.add_value(field_name="industries", value=json.dumps(job.get("industries", [])))
        loader.add_value(field_name="skills", value=job.get("skills"))
        loader.add_value(field_name="functions", value=job.get("functions", []))

        # Salary
        loader.add_value(field_name="minimum_salary", value=job.get("minSalary"))
        loader.add_value(field_name="maximum_salary", value=job.get("maximumSalary"))
        loader.add_value(field_name="salary_currency", value=job.get("currencyCode"))

        # Experience
        loader.add_value(field_name="minimum_experience", value=json.dumps(job.get("minimumExperience", {})))
        loader.add_value(field_name="maximum_experience", value=json.dumps(job.get("maximumExperience", {})))

        # Metadata
        loader.add_value(field_name="posted_by_text", value=job.get("postedBy"))
        loader.add_value(field_name="total_applicants", value=job.get("totalApplicants"))
        loader.add_value(field_name="created_at", value=job.get("createdAt"))
        loader.add_value(field_name="updated_at", value=job.get("updatedAt"))
        loader.add_value(field_name="closed_at", value=job.get("closedAt"))

        # Housekeeping
        loader.add_value(field_name="url", value=response.url)
        loader.add_value(field_name="project", value=self.settings.get("BOT_NAME"))
        loader.add_value(field_name="spider", value=self.name)
        loader.add_value(field_name="server", value=socket.gethostname())
        loader.add_value(field_name="date", value=datetime.datetime.now().isoformat())

        yield loader.load_item()
