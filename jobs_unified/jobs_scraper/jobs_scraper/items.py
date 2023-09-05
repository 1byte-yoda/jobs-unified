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
    apply_url_is_external = Field()
    apply_url = Field()

    # CompanyDetail
    company_overview = Field()
    company_photos = Field()
    company_avg_process_time = Field()
    company_dress_code = Field()
    company_employment_agency_number = Field()
    company_employment_agency_personnel_number = Field()
    company_facebook = Field()
    company_nearby_locations = Field()
    company_registration_no = Field()
    company_size = Field()
    company_telephone_number = Field()
    company_website = Field()
    company_video_url = Field()

    # JobHeader
    job_header_banner_url_large = Field()
    job_header_company_advertiser_id = Field()
    job_header_company_name = Field()
    job_header_company_slug = Field()
    job_header_company_url = Field()
    job_header_expiration_days = Field()
    job_header_is_internship = Field()
    job_header_job_title = Field()
    job_header_logo_url_small = Field()
    job_header_logo_url_medium = Field()
    job_header_logo_url_normal = Field()
    job_header_logo_url_large = Field()
    job_header_review = Field()
    job_header_posted_at = Field()
    job_header_posted_date_humanized = Field()
    job_header_salary_currency = Field()
    job_header_salary_extra_info = Field()
    job_header_salary_is_visible = Field()
    job_header_salary_max = Field()
    job_header_salary_min = Field()
    job_header_salary_type = Field()

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
    job_description = Field()
    job_requirements = Field()
    job_summary = Field()
    job_why_join_us = Field()

    # Location
    location = Field()

    # Housekeeping Fields
    url = Field()
    project = Field()
    spider = Field()
    server = Field()
    date = Field()
