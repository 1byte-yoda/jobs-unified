# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Field, Item


class JobStreetItem(Item):
    account_num = Field()
    ad_type = Field()
    advertisement_id = Field()

    # ApplyUrl
    apply_url = Field()

    # CompanyDetail
    company_detail = Field()

    # JobHeader
    job_header = Field()

    # Job
    job_id = Field()
    job_is_classified = Field()
    job_is_confidential = Field()
    job_is_expired = Field()
    job_title_slug = Field()
    job_page_url = Field()
    job_show_more_jobs = Field()
    job_source_country = Field()
    job_sub_account = Field()

    # JobDetail
    job_detail = Field()

    # Location
    job_location = Field()

    # Housekeeping Fields
    url = Field()
    project = Field()
    spider = Field()
    server = Field()
    date = Field()
