import math

import requests
import scrapy
from scrapy.http.response.html import HtmlResponse


class FoundItSpider(scrapy.Spider):
    URL = "https://www.foundit.com.ph/middleware/jobsearch?sort=1&limit=100&query=&locations=Philippines"
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9",
        "Referer": "http://www.foundit.com.ph/",
    }
    name = "foundit"

    @classmethod
    def get_total_pages(cls):
        response = requests.get(url=cls.URL, headers=cls.headers)
        if response.status_code >= 400:
            return 0

        response_json = response.json()
        total_jobs = response_json.get("meta", {}).get("paging", {}).get("total", 0)

        return int(math.ceil(total_jobs / 100) * 100)

    def start_requests(self):
        total_pages = self.get_total_pages()
        offset = 100
        for i in range(0, total_pages + offset, offset):
            url = f"{self.URL}&start={i}"
            yield scrapy.Request(url=url, headers=self.headers, callback=self.parse)

    def parse(self, response: HtmlResponse, **kwargs):
        response_json = response.json()

        if response_json.get("jobSearchStatus") == 200:
            jobs = response_json["jobSearchResponse"].get("data", [])

            for job in jobs[:3]:
                if "jobId" not in job:
                    continue

                job_url = f"http://www.foundit.com.ph{job['seoJdUrl']}"
                # TODO: Declare ItemLoader here and parse relevant fields
                # job_id - json response
                # company_name - json response
                # job_title - json response
                # job_exp - json response
                # employment_types - json response
                # location - json response
                # posted_by_text - json response
                # total_applicants - json response
                # created_at - json response
                # updated_at - json response
                # closed_at - json response
                # industries - json response
                # skills - json response
                # functions - json response
                # company_url - json response
                # minimum_salary - json response
                # maximum_salary - json response
                # salary_currency - json response
                # minimum_experience - json response
                # maximum_experience - json response

                yield scrapy.Request(url=job_url, headers=self.headers, callback=self.parse_job_item)

    def parse_job_item(self, response: HtmlResponse):
        pass
        # print(response.xpath("//div[contains(@id, 'jobDescription')]//text()").extract())  # job_description
