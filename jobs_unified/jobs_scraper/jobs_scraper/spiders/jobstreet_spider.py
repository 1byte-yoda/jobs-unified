import datetime
import json
import socket
from dataclasses import dataclass

import scrapy
import requests
from itemloaders.processors import TakeFirst
from scrapy.http.response.html import HtmlResponse
from scrapy.http.request.json_request import JsonRequest
from scrapy.loader import ItemLoader

from jobs_scraper.items import JobStreetItem


@dataclass(frozen=True)
class JobStreetGqlConfig:
    @staticmethod
    def get_gql_variables(job_id: str) -> dict:
        return {
            "jobId": job_id,
            "country": "ph",
            "locale": "en",
            "candidateId": "",
            "solVisitorId": ""
        }

    @staticmethod
    def get_gql_query() -> str:
        return """
        query 
        getJobDetail($jobId: String, $locale: String, $country: String, $candidateId: ID, $solVisitorId: String, $flight: String) {
          jobDetail(
            jobId: $jobId
            locale: $locale
            country: $country
            candidateId: $candidateId
            solVisitorId: $solVisitorId
            flight: $flight
          ) {
            id
            pageUrl
            jobTitleSlug
            applyUrl {
              url
              isExternal
            }
            isExpired
            isConfidential
            isClassified
            accountNum
            advertisementId
            subAccount
            showMoreJobs
            adType
            header {
              banner {
                bannerUrls {
                  large
                }
              }
              salary {
                max
                min
                type
                extraInfo
                currency
                isVisible
              }
              logoUrls {
                small
                medium
                large
                normal
              }
              jobTitle
              company {
                name
                url
                slug
                advertiserId
              }
              review {
                rating
                numberOfReviewer
              }
              expiration
              postedDate
              postedAt
              isInternship
            }
            companyDetail {
              companyWebsite
              companySnapshot {
                avgProcessTime
                registrationNo
                employmentAgencyPersonnelNumber
                employmentAgencyNumber
                telephoneNumber
                workingHours
                website
                facebook
                size
                dressCode
                nearbyLocations
              }
              companyOverview {
                html
              }
              videoUrl
              companyPhotos {
                caption
                url
              }
            }
            jobDetail {
              summary
              jobDescription {
                html
              }
              jobRequirement {
                careerLevel
                yearsOfExperience
                qualification
                fieldOfStudy
                industryValue {
                  value
                  label
                }
                skills
                employmentType
                languages
                postedDate
                closingDate
                jobFunctionValue {
                  code
                  name
                  children {
                    code
                    name
                  }
                }
                benefits
              }
              whyJoinUs
            }
            location {
              location
              locationId
              omnitureLocationId
            }
            sourceCountry
          }
        }
    """

    @classmethod
    def to_dict(cls, job_id: str) -> dict:
        return {"query": cls.get_gql_query(), "variables": cls.get_gql_variables(job_id=job_id)}


class JobStreetSpider(scrapy.Spider):
    URL = "https://www.jobstreet.com.ph/jobs"
    name = "jobstreet"

    def start_requests(self):
        total_pages = self.get_total_pages()

        urls = [f"{self.URL}?pg={i}" for i in range(1, total_pages + 1)]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    @classmethod
    def get_total_pages(cls):
        req_response = requests.get(cls.URL)
        response = HtmlResponse(url=cls.URL, body=req_response.text, encoding="utf-8")
        total_pages = int(response.xpath("//select[@id='pagination']//option//text()").extract()[-1])
        return total_pages

    def parse(self, response: HtmlResponse, **kwargs):
        job_links = response.xpath("//article[contains(@data-automation,'job-card-')]//a[contains(@href, 'job/')]//@href").extract()
        job_street_gql_url = "https://xapi.supercharge-srp.co/job-search/graphql?country=ph&isSmartSearch=true"

        for url in job_links:
            url_path, _ = url.split("?")
            job_id = url_path.split("-")[-1]
            yield JsonRequest(job_street_gql_url, method="POST", data=JobStreetGqlConfig.to_dict(job_id=job_id), callback=self.parse_job_card)

    def parse_job_card(self, response: HtmlResponse):
        item_json = response.json()

        loader = ItemLoader(item=JobStreetItem())
        loader.default_output_processor = TakeFirst()

        is_json_parsable = item_json.get("data") and item_json["data"].get("jobDetail")

        if is_json_parsable:
            # Job
            self.load_job_fields(loader=loader, item_json=item_json)

            # ApplyUrl
            self.load_apply_url_fields(loader=loader, item_json=item_json)

            # CompanyDetail
            self.load_apply_company_details_fields(loader=loader, item_json=item_json)

            # JobHeader
            self.load_job_header_fields(loader=loader, item_json=item_json)

            # JobDetail
            self.load_job_detail_fields(loader=loader, item_json=item_json)

            # Housekeeping
            self.load_housekeeping_fields(loader=loader, response=response)

        yield loader.load_item()

    def load_housekeeping_fields(self, loader: ItemLoader, response: HtmlResponse):
        loader.add_value(field_name="url", value=response.url)
        loader.add_value(field_name="project", value=self.settings.get("BOT_NAME"))
        loader.add_value(field_name="spider", value=self.name)
        loader.add_value(field_name="server", value=socket.gethostname())
        loader.add_value(field_name="date", value=datetime.datetime.now().isoformat())

    @staticmethod
    def load_job_fields(loader: ItemLoader, item_json: dict):
        job_detail = item_json["data"]["jobDetail"]
        if job_detail is not None:
            loader.add_value(field_name="job_id", value=job_detail["id"])
            loader.add_value(field_name="job_is_classified", value=job_detail["isClassified"])
            loader.add_value(field_name="job_is_confidential", value=job_detail["isConfidential"])
            loader.add_value(field_name="job_is_expired", value=job_detail["isExpired"])
            loader.add_value(field_name="job_title_slug", value=job_detail["jobTitleSlug"])
            loader.add_value(field_name="job_page_url", value=job_detail["pageUrl"])
            loader.add_value(field_name="job_show_more_jobs", value=job_detail["showMoreJobs"])
            loader.add_value(field_name="job_source_country", value=job_detail["sourceCountry"])
            loader.add_value(field_name="job_sub_account", value=job_detail["subAccount"])
            loader.add_value(field_name="account_num", value=job_detail["accountNum"])
            loader.add_value(field_name="ad_type", value=job_detail["adType"])
            loader.add_value(field_name="advertisement_id", value=job_detail["advertisementId"])

    @staticmethod
    def load_apply_url_fields(loader: ItemLoader, item_json: dict):
        apply_url = item_json["data"]["jobDetail"]["applyUrl"]
        loader.add_value(field_name="apply_url", value=apply_url)

    @staticmethod
    def load_apply_company_details_fields(loader: ItemLoader, item_json: dict):
        company_detail = item_json["data"]["jobDetail"]["companyDetail"]
        loader.add_value(field_name="company_detail", value=json.dumps(company_detail))

    @staticmethod
    def load_job_header_fields(loader: ItemLoader, item_json: dict):
        job_header = item_json["data"]["jobDetail"]["header"]
        loader.add_value(field_name="job_header", value=json.dumps(job_header))

    @staticmethod
    def load_job_detail_fields(loader: ItemLoader, item_json: dict):
        job_detail = item_json["data"]["jobDetail"]
        loader.add_value(field_name="job_detail", value=json.dumps(job_detail["jobDetail"]))
        loader.add_value(field_name="job_location", value=json.dumps(job_detail["location"]))
