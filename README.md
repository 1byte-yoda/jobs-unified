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

### Job Portals and Webscraping Strategies
- Indeed
  - API Request + XPath
- JobStreet
  - The data was parsed from a paginated Graphql API which returns json data.
  - Each page is a json data consists of 30 jobs.
  - I retained all JSON fields of type JSON in their original form as I want to also showcase how it can be transformed in the silver layer
  but practically speaking, it is good to do all the data standardization in a centralize layer ie. silver layer so that modification can be done in a single place
  - This will output a single file in `bronze/jobstreet/{yyyy}/{mm}/{dd}/{HHMM}/{spider.name}-{uuid4()}-{yyyymmddHHMM}.parquet` path with a disk size less than 100mb.
  - If the file grew bigger and optimization is required to leverage ADLS gen2's performance, we can tweak the `FEED_EXPORT_BATCH_ITEM_COUNT` scrapy settings.
  Or we can leave the data sharding/bucketing to the silver/gold layer
- LinkedIn
  - HTML Request + XPath
- FoundIt
  - API Request + XPath