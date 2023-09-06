import datetime
import json
import socket
from pprint import pprint

import scrapy
from itemloaders.processors import TakeFirst
from scrapy.http.response.html import HtmlResponse
from scrapy.http.request.json_request import JsonRequest
from scrapy.loader import ItemLoader
import requests

from jobs_scraper.items import JobStreetItem


def get_gql_variables(job_id: str) -> dict:
    return {"jobId": job_id,
            "country": "ph",
            "locale": "en",
            "candidateId": "",
            "solVisitorId": ""
            }


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


def get_gql_payload(job_id: str) -> dict:
    return {"query": get_gql_query(), "variables": get_gql_variables(job_id=job_id)}


class JobStreetSpider(scrapy.Spider):
    URL = "https://www.jobstreet.com.ph/jobs"
    name = "jobstreet"

    def start_requests(self):
        url = self.URL
        total_pages = 2  # self.get_total_pages()

        urls = [f"{url}?pg={i}" for i in range(1, total_pages + 1)]
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

        for url in [job_links[0]]:
            url_path, _ = url.split("?")
            job_id = url_path.split("-")[-1]
            yield JsonRequest(job_street_gql_url, method="POST", data=get_gql_payload(job_id=job_id), callback=self.parse_job_card)

    def parse_job_card(self, response: HtmlResponse):
        item_json = response.json()

        loader = ItemLoader(item=JobStreetItem())
        loader.default_output_processor = TakeFirst()

        # Job
        loader.add_value(field_name="account_num", value=item_json["data"]["jobDetail"]["accountNum"])
        loader.add_value(field_name="ad_type", value=item_json["data"]["jobDetail"]["adType"])
        loader.add_value(field_name="advertisement_id", value=item_json["data"]["jobDetail"]["advertisementId"])

        # ApplyUrl
        loader.add_value(field_name="apply_url_is_external", value=item_json["data"]["jobDetail"]["applyUrl"]["isExternal"])
        loader.add_value(field_name="apply_url", value=item_json["data"]["jobDetail"]["applyUrl"]["url"])

        # CompanyDetail
        loader.add_value(field_name="company_overview", value=item_json["data"]["jobDetail"]["companyDetail"]["companyOverview"]["html"])
        loader.add_value(field_name="company_photos", value=item_json["data"]["jobDetail"]["companyDetail"]["companyPhotos"])
        loader.add_value(field_name="company_avg_process_time", value=item_json["data"]["jobDetail"]["companyDetail"]["companySnapshot"]["avgProcessTime"])
        loader.add_value(field_name="company_dress_code", value=item_json["data"]["jobDetail"]["companyDetail"]["companySnapshot"]["dressCode"])
        loader.add_value(field_name="company_employment_agency_number", value=item_json["data"]["jobDetail"]["companyDetail"]["companySnapshot"]["employmentAgencyNumber"])
        loader.add_value(field_name="company_employment_agency_personnel_number", value=item_json["data"]["jobDetail"]["companyDetail"]["companySnapshot"]["employmentAgencyPersonnelNumber"])
        loader.add_value(field_name="company_facebook", value=item_json["data"]["jobDetail"]["companyDetail"]["companySnapshot"]["facebook"])
        loader.add_value(field_name="company_nearby_locations", value=item_json["data"]["jobDetail"]["companyDetail"]["companySnapshot"]["nearbyLocations"])
        loader.add_value(field_name="company_registration_no", value=item_json["data"]["jobDetail"]["companyDetail"]["companySnapshot"]["registrationNo"])
        loader.add_value(field_name="company_size", value=item_json["data"]["jobDetail"]["companyDetail"]["companySnapshot"]["size"])
        loader.add_value(field_name="company_telephone_number", value=item_json["data"]["jobDetail"]["companyDetail"]["companySnapshot"]["telephoneNumber"])
        loader.add_value(field_name="company_website", value=item_json["data"]["jobDetail"]["companyDetail"]["companySnapshot"]["website"])
        loader.add_value(field_name="company_working_hours", value=item_json["data"]["jobDetail"]["companyDetail"]["companySnapshot"]["workingHours"])
        loader.add_value(field_name="company_video_url", value=item_json["data"]["jobDetail"]["companyDetail"]["videoUrl"])

        # JobHeader
        loader.add_value(field_name="job_header_banner_url_large", value=item_json["data"]["jobDetail"]["header"]["banner"]["bannerUrls"]["large"])
        loader.add_value(field_name="job_header_company_advertiser_id", value=item_json["data"]["jobDetail"]["header"]["company"]["advertiserId"])
        loader.add_value(field_name="job_header_company_name", value=item_json["data"]["jobDetail"]["header"]["company"]["name"])
        loader.add_value(field_name="job_header_company_slug", value=item_json["data"]["jobDetail"]["header"]["company"]["slug"])
        loader.add_value(field_name="job_header_company_url", value=item_json["data"]["jobDetail"]["header"]["company"]["url"])
        loader.add_value(field_name="job_header_expiration_days", value=item_json["data"]["jobDetail"]["header"]["expiration"])
        loader.add_value(field_name="job_header_is_internship", value=item_json["data"]["jobDetail"]["header"]["isInternship"])
        loader.add_value(field_name="job_header_job_title", value=item_json["data"]["jobDetail"]["header"]["jobTitle"])
        loader.add_value(field_name="job_header_logo_url_small", value=item_json["data"]["jobDetail"]["header"]["logoUrls"]["small"])
        loader.add_value(field_name="job_header_logo_url_medium", value=item_json["data"]["jobDetail"]["header"]["logoUrls"]["medium"])
        loader.add_value(field_name="job_header_logo_url_normal", value=item_json["data"]["jobDetail"]["header"]["logoUrls"]["normal"])
        loader.add_value(field_name="job_header_logo_url_large", value=item_json["data"]["jobDetail"]["header"]["logoUrls"]["large"])
        loader.add_value(field_name="job_header_review", value=item_json["data"]["jobDetail"]["header"]["review"])
        loader.add_value(field_name="job_header_posted_at", value=item_json["data"]["jobDetail"]["header"]["postedAt"])
        loader.add_value(field_name="job_header_posted_date_humanized", value=item_json["data"]["jobDetail"]["header"]["postedDate"])
        loader.add_value(field_name="job_header_salary_currency", value=item_json["data"]["jobDetail"]["header"]["salary"]["currency"])
        loader.add_value(field_name="job_header_salary_extra_info", value=item_json["data"]["jobDetail"]["header"]["salary"]["extraInfo"])
        loader.add_value(field_name="job_header_salary_is_visible", value=item_json["data"]["jobDetail"]["header"]["salary"]["isVisible"])
        loader.add_value(field_name="job_header_salary_max", value=item_json["data"]["jobDetail"]["header"]["salary"]["max"])
        loader.add_value(field_name="job_header_salary_min", value=item_json["data"]["jobDetail"]["header"]["salary"]["min"])
        loader.add_value(field_name="job_header_salary_type", value=item_json["data"]["jobDetail"]["header"]["salary"]["type"])

        # Job
        loader.add_value(field_name="job_id", value=item_json["data"]["jobDetail"]["id"])
        loader.add_value(field_name="job_is_classified", value=item_json["data"]["jobDetail"]["isClassified"])
        loader.add_value(field_name="job_is_confidential", value=item_json["data"]["jobDetail"]["isConfidential"])
        loader.add_value(field_name="job_is_expired", value=item_json["data"]["jobDetail"]["isExpired"])
        loader.add_value(field_name="job_title_slug", value=item_json["data"]["jobDetail"]["jobTitleSlug"])
        loader.add_value(field_name="job_page_url", value=item_json["data"]["jobDetail"]["pageUrl"])
        loader.add_value(field_name="job_show_more_jobs", value=item_json["data"]["jobDetail"]["showMoreJobs"])
        loader.add_value(field_name="job_source_country", value=item_json["data"]["jobDetail"]["sourceCountry"])
        loader.add_value(field_name="job_sub_account", value=item_json["data"]["jobDetail"]["subAccount"])

        # JobDetail
        loader.add_value(field_name="job_description", value=item_json["data"]["jobDetail"]["jobDetail"]["jobDescription"]["html"])
        loader.add_value(field_name="job_requirements", value=item_json["data"]["jobDetail"]["jobDetail"]["jobRequirement"])
        loader.add_value(field_name="job_summary", value=item_json["data"]["jobDetail"]["jobDetail"]["summary"])
        loader.add_value(field_name="job_why_join_us", value=item_json["data"]["jobDetail"]["jobDetail"]["whyJoinUs"])

        # Location
        loader.add_value(field_name="job_location", value=item_json["data"]["jobDetail"]["location"])

        # Housekeeping Fields
        loader.add_value(field_name="url", value=response.url)
        loader.add_value(field_name="project", value=self.settings.get("BOT_NAME"))
        loader.add_value(field_name="spider", value=self.name)
        loader.add_value(field_name="server", value="local")  # socket.gethostname()
        loader.add_value(field_name="date", value=datetime.datetime.now().isoformat())

        yield loader.load_item()
