import json

import scrapy
from scrapy.http.response.html import HtmlResponse
from scrapy.http.request.json_request import JsonRequest
import requests


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

        for url in job_links:
            url_path, _ = url.split("?")
            job_id = url_path.split("-")[-1]
            yield JsonRequest(job_street_gql_url, method="POST", data=get_gql_payload(job_id=job_id), callback=self.parse_job_card)

    @staticmethod
    def parse_job_card(response: HtmlResponse):
        item = response.json()
        print(item)
