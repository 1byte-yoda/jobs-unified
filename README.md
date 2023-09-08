## Jobs Unified

### Why Create Jobs Unified?
Applying for a job can become overwhelming nowadays, as companies posts scattered job advertisements across the internet. And as technology advances, more and more employers
are adopting to the latest technical trends which makes the job requirements and job titles in various industries gets inflated.
Jobs Unified aims to help consolidate these jobs from various job portals to make it easier to monitor and get notified with new job posts and updates.
On top of that, it will be interesting to take a look onto various analyses that will help make good decisions when applying for a new role, and also to
make a good sense on where the job market is leading in regard to the technological trends particularly in the Philippines.

### Who will benefit from this project?
This shall benefit those who are looking for a job in the Data Science and Analytics industry within the following Job Portals:
1. [Indeed PH](https://ph.indeed.com)
2. [Jobstreet PH](https://jobstreet.com.ph)
3. [Linkedin](https://linkedin.com)
4. [FoundIt PH](https://foundit.com)

### Visualizations (Workflows, ERDs)

### The value of this project will bring
With the saturated job market, this project can help job applicants to gain insights on their data science and analytics related job(s) of interest and make
sound decision and use that in their competitive advantage.

### Project Specifications
#### Data Ingestion Requirements
- Ingest all 4 data sources into the data lake
- Ingested data must have the schema applied
- Ingested data must have the following audit columns:
  - Ingested Date
  - Source name
- Ingested data must be stored in Parquet Format
- Must be able to analyze the ingested data via SQL
- Ingestion logic must be able to handle incremental load
- Schema validation
  - Failed data validation must be handled for auditing

#### Data Transformation Requirements
- Join the key information required for reporting to create a new table
- Join the key information required for analysis to create a new table
- Transformed tables must have audit columns
- Must be able to analyze the transformed data via SQL
- Transformed tables must be stored in Parquet format
- Transformation logic must be able to handle incremental load
- Deduplication of the job
  - Record how many times it was duplicated

#### Reporting Requirements
- Create a hierarchy funnel (high level up to the granular details)
1. What job titles will give a higher chance of getting an interview?
   - Top 20 in-demand job titles for monthly and yearly view
2. What technical skills are crucial to be a great fit for the data engineer role?
   - Most Common Technical Skill requirements for data engineers monthly and yearly
3. How many companies provides the salary information upfront?
   - Number of Jobs with and without salary information
4. How many companies are adopting to a remote work set up?
   - Comparison of work set up between remote, hybrid, and on-site
5. Which companies has a huge demand for a data engineer / data analyst / data science roles?
   - Top 10 Companies with most data related job advertisements
6. How high is the barrier for a data engineer job?
   - Number of Data Engineering Jobs based on seniority
   - Data Engineering skills based on seniority
7. Which companies needs to fill a data engineer role immediately
   - Top 10 Data Engineer Jobs per company posted on multiple job portals
8. Data Profiling
   - Number of null values per column
   - Columns with weird values
   - Missing columns
   - Data Freshness
   - Column Format Variance

#### Analysis Requirements
1. Which type of companies usually use AWS vs. Azure?
   - Industry wise
   - Large or SMEs
2. What is the correlation between the amount of information in a job post and the amount of salary offered?
3. Are companies using an appropriate job titles correctly?
   - For instance, Skills and Responsibilities of Python Developers vs. Data Engineers

#### Non-functional Specifications
#### Scheduling
- Schedule to run daily every 7am and 8pm
- Ability to monitor pipeline executions
- Ability to re-run failed pipelines
- Ability to set up alerts for failed pipelines

#### Other
- Ability to delete individual records in datalake
- Ability to see history and time travel
- Ability to roll back to a previous version

#### Architectural Decisions
- Star Schema
- Medallion Architecture
- Handling dimensional Updates
  - SCD Type 2
- Tools
  - ADF
  - ADLS Gen2
  - Synapse spark pool
  - Synapse dedicated
- File Format
  - Parquet File Format
- Compression Format
  - Snappy
- Physical Data Model
  - Fact Tables
    - xxxx
  - Dimension Tables
    - xxxx
  - Distribution Types (Why?)
  - Index (Why?)
  - Partitioning column (Why?)
  - Bucketing column (Why?)
- Data Governance (Purview)
- Data Security (Apply to next project)
- Power BI
- Devops?

### Scrapy Spiders
- Each job portal uses a dedicated Scrapy Spider to crawl for jobs
- Each Spider will output a single file in `bronze/{JOB_PORTAL_NAME}/{yyyy}/{mm}/{dd}/{HHMM}/{spider.name}-{uuid4()}-{yyyymmddHHMM}.parquet` path with a disk size ~100mb.
- If the file grew bigger and optimization is required to leverage ADLS gen2's performance, we can tweak the `FEED_EXPORT_BATCH_ITEM_COUNT` scrapy settings.
  Or we can leave the data sharding/bucketing to the silver/gold layer

#### Job Portals and Webscraping Strategies
- Indeed
  - Indeed presents some scraping challenges along the way. It has a cloudflare protected server origin which makes it challenging to scrape, so I had to iterate and experiment a bit to make it work.
  - Each page is represented by HTML and has 15 jobs.
  - Before starting the traversal of job HTML elements to get the fields that I need, I tried to look first if they have a REST endpoint that will make my task easier.
  - Indeed provides a REST endpoint to GET a specific Job, but I believe it requires the creation of custom Scrapy Middleware which will require tedious effort.
  - As a last resort, I found out an easier way. The HTML source of each job already contains the JSON data used to populate each field in the job posting which I can use to parse and query each field
  - Transformation wise, I have flattened the important JSON fields in question, and retain the rest of the fields – good to have.
  - After carefully inspecting the JSON response, some fields were obviously used as a metadata to render Javascript objects, hence, only 21 out of 112 fields were retained which suites usability in this project.
  - Even though the total jobs count is given, Indeed was limiting its pagination until page 70 only.
  - How I managed to scrape their cloudflare protected website?
    - I first tried `scrapy-selenium` package to render each page's content and then work on top of that
    - I also had to make a middleware that will handle cloudflare restrictions, I initially used the `cloudscraper` package to do it – redirecting every response into it whenever a cloudflare challenge occurs.
    Even so, cloudflare still detects the scraping activity, thus, blocked some of the requests sent over their `/viewJob` endpoint.
    - After some research there is a more up-to-date robust solution called `FlareSolverr`. It starts a proxy server, and it waits for user requests in an idle state using few resources.
    When some request arrives, it uses Selenium with the `undetected-chromedriver` to create a web browser (Chrome)

- JobStreet
  - The data was parsed from a paginated Graphql API which returns json data.
  - Each page is represented by a json data consists of 30 jobs.
  - I retained all JSON fields of type JSON in their original form as I want to also showcase how it can be transformed in the silver layer
  but practically speaking, it is good to do all the data standardization in a centralize layer ie. silver layer so that modification can be done in a single place
  
- LinkedIn
  - Linkedin has a cumbersome jobs web portal which makes it challenging to use even the creative way of scraping like Selenium or the Cloudflare bypass tool I used – FlareSolver.
  - I first tried using the Selenium driver to parse the html content and traverse the fields I need using xpath, but along the way, Linkedin is smart enough to detect a bot scraping their website
  so, you'll get blocked for a while until it returns back – this resulted into a limited amount of jobs scraped. The retry mechanism in scrapy was not enough to solve this. I might try to tweak
  the throttling mechanism a bit to see if it will work better.
  - I tried a better approach for scraping linkedin jobs by using FlareSolverr: This didn't work as I keep on getting blocked with 403 response so I continued using the selenium linkedin scraper.

- FoundIt
  - API Request + XPath