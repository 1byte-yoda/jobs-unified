from scrapy import Field, Item


class HousekeepingItem(Item):
    url = Field()
    project = Field()
    spider = Field()
    server = Field()
    date = Field()


# class IndeedItem(HousekeepingItem):
#     # BaseSalary
#     base_salary_currency = Field()
#     base_salary_unit_text = Field()
#     base_salary_min = Field()
#     base_salary_max = Field()
#
#     # Job
#     job_key = Field()
#     job_date_posted = Field()
#     job_description = Field()
#     is_direct_apply = Field()
#     job_employment_type = Field()
#     job_title = Field()
#
#     # Location
#     job_location_country = Field()
#     job_location_locality = Field()
#     job_location_region = Field()
#
#     date_valid_through = Field()

class IndeedItem(HousekeepingItem):
    base_url = Field()
    benefits_model = Field()
    country = Field()
    hiring_insights_model = Field()
    job_info_wrapper_model = Field()
    job_key = Field()
    job_location = Field()
    job_metadata_footer_model = Field()
    job_title = Field()
    language = Field()
    locale = Field()
    request_path = Field()
    salary_info_model = Field()


# class IndeedItem(HousekeepingItem):
#     base_url: str = field(default="https://ph.indeed.com")
#     benefits_model: Optional[str] = field(default=None)
#     categorized_attribute_model: Optional[str] = field(default=None)
#     cmi_job_category_model: Optional[str] = field(default=None)
#     commute_info_model: Optional[str] = field(default=None)
#     company_avatar_model: Optional[str] = field(default=None)
#     company_follow_form_model: Optional[str] = field(default=None)
#     company_tab_model: Optional[str] = field(default=None)
#     contact_person_model: Optional[str] = field(default=None)
#     country: str = field(default="PH")
#     indeed_apply_button_container: dict = field(default_factory=dict)
#     job_info_wrapper_model: dict = field(default_factory=dict)
#     job_key: Optional[str] = field(default=None)
#     job_location: Optional[str] = field(default=None)
#     job_metadata_footer_model: dict = field(default_factory=dict)
#     job_title: Optional[str] = field(default=None)
#     language: Optional[str] = field(default=None)
#     last_visit_time: Optional[int] = field(default=None)
#     lazy_providers: dict = field(default_factory=dict)
#     locale: Optional[str] = field(default=None)
#     request_path: Optional[str] = field(default=None)
#     salary_info_model: dict = field(default_factory=dict)
#     logged_in: bool
#     account_key: Optional[str]
#     apply_button_sdk_enabled: bool
#     additional_links_view_model: dict
#     api_paths: dict
#     apollo_cached_response: List[dict]
#     app_common_data: Optional[str]
#     auto_click_apply: bool
#     base64_encoded_json: str
#     base_inbox_url: str
#     call_to_interview_button_model: Optional[str]
#     chatbot_apply_button_model: Optional[str]
#     client_side_proctor_groups: dict
#     collapsed_description_payload: dict
#     css_reset_providers: dict
#     ctk: str
#     dcm_model: dict
#     dg_token: str
#     download_app_button_model: Optional[str]
#     desktop: bool
#     dislike_from_2pane_enabled: bool
#     dsanr: bool
#     employer_responsive_card_model: Optional[str]
#     from_: str
#     globalnavFooterHTML: str
#     globalnavHeaderHTML: str
#     high_quality_market_place: Optional[str]
#     high_quality_market_place_hiring_manager: Optional[str]
#     hiring_insights_model: dict
#     indeed_logo_model: Optional[str]
#     indeedLogoModel: Optional[str]
#     inlineJsErrEnabled: bool
#     isApp: bool
#     isApplyTextColorChanges: bool
#     isApplyTextSizeChanges: bool
#     isCriOS: bool
#     isDislikeFormV2Enabled: bool
#     isSafariForIOS: bool
#     isSalaryNewDesign: bool
#     isSyncJobs: bool
#     asJobViewPingModel: dict
#     jasxInputWhatWhereActive: bool
#     jobAlertSignInModalModel: Optional[str]
#     jobAlertSignUp: Optional[str]
#     jobCardStyleModel: dict
#     job_seen_data: str
#     localeData: dict
#     mob_resource_timing_enabled: bool
#     mob_tk: str
#     mosaicData: dict
#     oneGraphApiKey: str
#     oneGraphApiUrl: str
#     original_job_link_model: Optional[str]
#     pageId: str
#     parenttk: "1h9noh658h0og801"
#     phoneLinkType: Optional[str]
#     preciseLocationModel: Optional[str]
#     profileBaseUrl: str
#     queryString: Optional[str]
#     recentQueryString: str
#     recommendedJobsModel: dict
#     recommendedSearchesModel: dict
#     relatedLinks: Optional[str]
#     resumeFooterModel: dict
#     resumePromoCardModel: Optional[str]
#     rtl: bool
#     salaryGuideModel: dict
#     saveJobButtonContainerModel: dict
#     saveJobFailureModalModel: dict
#     saveJobLimitExceededModalModel: dict
#     segmentId: Optional[str]
#     segmentPhoneNumberButtonLinkModel: Optional[str]
#     shareJobButtonContainerModel: dict
#     shouldLogResolution: bool
#     shouldShowConditionalBackButton: bool
#     showEmployerResponsiveCard: bool
#     showGlobalNavContent: bool
#     showReportInJobButtons: bool
#     sponsored: bool
#     staticPrefix: str
#     stickyType: str
#     successfullySignedInModel: Optional[str]
#     thirdPartyAndMobile: bool
#     thirdPartyQuestionsToggle: bool
#     viewJobButtonLinkContainerModel: Optional[str]
#     viewJobDisplay: str
#     viewJobDisplayParam: str
#     viewjobDislikes: bool
#     whatWhereFormModel: Optional[str]
#     workplaceInsightsModel: Optional[str]
#     zoneProviders: dict


class JobStreetItem(HousekeepingItem):
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


class LinkedinItem(HousekeepingItem):
    company_img_url = Field()
    company_url = Field()
    company_name = Field()

    job_title = Field()
    location = Field()
    job_description = Field()
    posted_time_ago = Field()
    num_applicants = Field()
    seniority_level = Field()
    employment_type = Field()
    job_function = Field()
    job_industries = Field()


class FoundItItem(HousekeepingItem):
    company_name = Field()
    job_id = Field()
    job_title = Field()
    job_exp = Field()
    job_description = Field()
    employment_types = Field()
    locations = Field()
    posted_by_text = Field()
    total_applicants = Field()
    created_at = Field()
    updated_at = Field()
    closed_at = Field()
    industries = Field()
    skills = Field()
    functions = Field()
    company_url = Field()
    minimum_salary = Field()
    maximum_salary = Field()
    salary_currency = Field()
    minimum_experience = Field()
    maximum_experience = Field()
