import datetime
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
        url = self.URL
        total_pages = self.get_total_pages()

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
            yield JsonRequest(job_street_gql_url, method="POST", data=JobStreetGqlConfig.to_dict(job_id=job_id), callback=self.parse_job_card)

    def parse_job_card(self, response: HtmlResponse):
        item_json = response.json()

        loader = ItemLoader(item=JobStreetItem())
        loader.default_output_processor = TakeFirst()

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
        loader.add_value(field_name="server", value="local")  # socket.gethostname()
        loader.add_value(field_name="date", value=datetime.datetime.now().isoformat())

    @staticmethod
    def load_job_fields(loader: ItemLoader, item_json: dict):
        job_detail = item_json["data"]["jobDetail"]
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
        loader.add_value(field_name="apply_url_is_external", value=apply_url["isExternal"])
        loader.add_value(field_name="apply_url", value=apply_url["url"])

    @staticmethod
    def load_apply_company_details_fields(loader: ItemLoader, item_json: dict):
        company_detail = item_json["data"]["jobDetail"]["companyDetail"]
        loader.add_value(field_name="company_overview", value=company_detail["companyOverview"]["html"])
        loader.add_value(field_name="company_photos", value=company_detail["companyPhotos"])
        loader.add_value(field_name="company_avg_process_time", value=company_detail["companySnapshot"]["avgProcessTime"])
        loader.add_value(field_name="company_dress_code", value=company_detail["companySnapshot"]["dressCode"])
        loader.add_value(field_name="company_employment_agency_number", value=company_detail["companySnapshot"]["employmentAgencyNumber"])
        loader.add_value(field_name="company_employment_agency_personnel_number", value=company_detail["companySnapshot"]["employmentAgencyPersonnelNumber"])
        loader.add_value(field_name="company_facebook", value=company_detail["companySnapshot"]["facebook"])
        loader.add_value(field_name="company_nearby_locations", value=company_detail["companySnapshot"]["nearbyLocations"])
        loader.add_value(field_name="company_registration_no", value=company_detail["companySnapshot"]["registrationNo"])
        loader.add_value(field_name="company_size", value=company_detail["companySnapshot"]["size"])
        loader.add_value(field_name="company_telephone_number", value=company_detail["companySnapshot"]["telephoneNumber"])
        loader.add_value(field_name="company_website", value=company_detail["companySnapshot"]["website"])
        loader.add_value(field_name="company_working_hours", value=company_detail["companySnapshot"]["workingHours"])
        loader.add_value(field_name="company_video_url", value=company_detail["videoUrl"])

    @staticmethod
    def load_job_header_fields(loader: ItemLoader, item_json: dict):
        job_header = item_json["data"]["jobDetail"]["header"]
        loader.add_value(field_name="job_header_banner_url_large", value=job_header["banner"]["bannerUrls"]["large"])
        loader.add_value(field_name="job_header_company_advertiser_id", value=job_header["company"]["advertiserId"])
        loader.add_value(field_name="job_header_company_name", value=job_header["company"]["name"])
        loader.add_value(field_name="job_header_company_slug", value=job_header["company"]["slug"])
        loader.add_value(field_name="job_header_company_url", value=job_header["company"]["url"])
        loader.add_value(field_name="job_header_expiration_days", value=job_header["expiration"])
        loader.add_value(field_name="job_header_is_internship", value=job_header["isInternship"])
        loader.add_value(field_name="job_header_job_title", value=job_header["jobTitle"])
        loader.add_value(field_name="job_header_logo_url_small", value=job_header["logoUrls"]["small"])
        loader.add_value(field_name="job_header_logo_url_medium", value=job_header["logoUrls"]["medium"])
        loader.add_value(field_name="job_header_logo_url_normal", value=job_header["logoUrls"]["normal"])
        loader.add_value(field_name="job_header_logo_url_large", value=job_header["logoUrls"]["large"])
        loader.add_value(field_name="job_header_review", value=job_header["review"])
        loader.add_value(field_name="job_header_posted_at", value=job_header["postedAt"])
        loader.add_value(field_name="job_header_posted_date_humanized", value=job_header["postedDate"])
        loader.add_value(field_name="job_header_salary_currency", value=job_header["salary"]["currency"])
        loader.add_value(field_name="job_header_salary_extra_info", value=job_header["salary"]["extraInfo"])
        loader.add_value(field_name="job_header_salary_is_visible", value=job_header["salary"]["isVisible"])
        loader.add_value(field_name="job_header_salary_max", value=job_header["salary"]["max"])
        loader.add_value(field_name="job_header_salary_min", value=job_header["salary"]["min"])
        loader.add_value(field_name="job_header_salary_type", value=job_header["salary"]["type"])

    @staticmethod
    def load_job_detail_fields(loader: ItemLoader, item_json: dict):
        job_detail = item_json["data"]["jobDetail"]
        loader.add_value(field_name="job_description", value=job_detail["jobDetail"]["jobDescription"]["html"])
        loader.add_value(field_name="job_requirements", value=job_detail["jobDetail"]["jobRequirement"])
        loader.add_value(field_name="job_summary", value=job_detail["jobDetail"]["summary"])
        loader.add_value(field_name="job_why_join_us", value=job_detail["jobDetail"]["whyJoinUs"])
        loader.add_value(field_name="job_location", value=job_detail["location"])
