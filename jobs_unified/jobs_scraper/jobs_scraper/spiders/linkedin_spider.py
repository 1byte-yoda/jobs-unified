import datetime
import random
import socket

import scrapy
from scrapy.http.response.html import HtmlResponse
from itemloaders import ItemLoader
from itemloaders.processors import TakeFirst
from scrapy_selenium import SeleniumRequest

from jobs_scraper.items import LinkedinItem


class LinkedInSpider(scrapy.Spider):
    URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=&location=Philippines&geoId=103121230&trk=public_jobs_jobs-search-bar_search-submit&position=1&pageNum=0&start="
    name = "linkedin"

    def start_requests(self):
        page_num = 0
        yield SeleniumRequest(url=f"{self.URL}{page_num}", callback=self.parse, cb_kwargs={"page_num": page_num})

    def parse(self, response: HtmlResponse, **kwargs):
        page_num = kwargs["page_num"] + 25

        job_urls = response.xpath("//*[contains(@data-entity-urn, 'jobPosting')]/a/@href").extract()

        for url in job_urls:
            yield SeleniumRequest(url=url, callback=self.parse_job_item, wait_time=random.randint(1, 8))

        if len(job_urls) > 0:
            yield SeleniumRequest(url=f"{self.URL}{page_num}", callback=self.parse, cb_kwargs={"page_num": page_num})

    def parse_job_item(self, response: HtmlResponse):
        loader = ItemLoader(item=LinkedinItem())
        loader.default_output_processor = TakeFirst()

        loader.add_value("company_img_url", response.xpath("//a[@data-tracking-control-name='public_jobs_topcard_logo']/img/@src").extract_first())
        loader.add_value("company_url", response.xpath("//a[contains(@data-tracking-control-name, 'public_jobs_topcard-org-name')]/@href").extract_first())
        loader.add_value("company_name", response.xpath("//a[contains(@data-tracking-control-name, 'public_jobs_topcard-org-name')]/text()").extract_first())

        loader.add_value("job_title", response.xpath("//*[contains(@class, 'topcard__title')]//text()").extract_first())
        loader.add_value("location", response.xpath("//span[contains(@class, 'topcard__flavor--bullet')]/text()").extract_first())
        loader.add_value("job_description", response.xpath("//div[contains(@class, 'description__text')]/section//text()").extract())
        loader.add_value("posted_time_ago", response.xpath("//span[contains(@class, 'posted-time-ago')]//text()").extract_first())
        loader.add_value("num_applicants", "".join(response.xpath("//*[contains(@class, 'num-applicants')]//text()").extract()))
        job_criteria = response.xpath("//span[contains(@class, 'description__job-criteria-text')]//text()").extract()
        loader.add_value("seniority_level", job_criteria[0] if job_criteria else "Not Applicable")
        loader.add_value("employment_type", job_criteria[1] if job_criteria else "Not Applicable")
        loader.add_value("job_function", job_criteria[2] if job_criteria else "Not Applicable")
        loader.add_value("job_industries", job_criteria[3] if job_criteria else "Not Applicable")

        loader.add_value(field_name="url", value=response.url)
        loader.add_value(field_name="project", value=self.settings.get("BOT_NAME"))
        loader.add_value(field_name="spider", value=self.name)
        loader.add_value(field_name="server", value=socket.gethostname())
        loader.add_value(field_name="date", value=datetime.datetime.now().isoformat())

        yield loader.load_item()
