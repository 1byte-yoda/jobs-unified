import pytest
import requests
import json

from jobs_scraper.spiders.indeed_flare_scraper import IndeedFlareSpider
from jobs_unified.jobs_scraper.jobs_scraper.spiders.jobstreet_spider import JobStreetSpider
from scrapy.http.response.html import HtmlResponse


jobstreet_item_keys = [
    "job_id",
    "job_is_classified",
    "job_is_confidential",
    "job_is_expired",
    "job_page_url",
    "job_source_country",
    "account_num",
    "ad_type",
    "advertisement_id",
    "apply_url",
    "company_detail",
    "job_header",
    "job_detail",
    "job_location",
    "url",
    "project",
    "spider",
    "server",
    "date"
]

indeed_item_keys = ['base_url',
                    'benefits_model',
                    'country',
                    'hiring_insights_model',
                    'job_info_wrapper_model',
                    'job_key',
                    'job_location',
                    'job_metadata_footer_model',
                    'job_title',
                    'language',
                    'locale',
                    'request_path',
                    'salary_info_model',
                    'url',
                    'project',
                    'spider',
                    'server',
                    'date']


@pytest.mark.parametrize(
    "url,expected",
    [("https://www.jobstreet.com.ph/jobs?pg=1",  jobstreet_item_keys)]
)
def test_gql_api_schema_did_not_changed(url, expected):
    spider = JobStreetSpider(settings={"BOT_NAME": "test_spider"})
    job_list_response = requests.get(url)
    scrapy_response = HtmlResponse(url=url, body=job_list_response.text, encoding="utf-8")

    result = list(spider.parse(scrapy_response))

    # 1 job page has 30 job cards
    assert len(result) == 30

    for r in result:
        job_card_response = requests.post(url=r.url, json=json.loads(r.body))
        jobstreet_item: dict = next(spider.parse_job_card(response=HtmlResponse(url=r.url, body=job_card_response.text, encoding="utf-8")))
        assert list(jobstreet_item.keys()) == expected


@pytest.mark.parametrize(
    "url,expected",
    [("https://ph.indeed.com/jobs?filter=0&q=all&l=Philippines&start=0",  indeed_item_keys)]
)
def test_indeed_json_response_did_not_changed(url, expected):
    flare_base_url = "http://localhost:8191/v1"
    flare_headers = {'Content-Type': 'application/json'}

    spider = IndeedFlareSpider(settings={"BOT_NAME": "test_spider"})
    post_body = {'cmd': 'request.get', 'url': url, 'maxTimeout': 60000}
    job_list_response = requests.post(flare_base_url, headers=flare_headers, json=post_body)
    scrapy_response = HtmlResponse(url=url, body=job_list_response.text, encoding="utf-8")

    result = list(spider.parse(scrapy_response))

    # 1 job page has 15 jobs
    assert len(result) == 15

    for r in result:
        response_body = json.loads(r.body)
        post_body = {'cmd': 'request.get', 'url': response_body["url"], 'maxTimeout': 60000}
        job_card_response = requests.post(url=r.url, headers=flare_headers, json=post_body)
        indeed_item: dict = next(spider.parse_job_card(response=HtmlResponse(url=response_body["url"], body=job_card_response.text, encoding="utf-8")))
        assert list(indeed_item.keys()) == expected
