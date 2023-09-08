import pathlib
from chromedriver_py import binary_path

BOT_NAME = "jobs_scraper"

SPIDER_MODULES = ["jobs_scraper.spiders"]
NEWSPIDER_MODULE = "jobs_scraper.spiders"

# Selenium
SELENIUM_DRIVER_NAME = 'chrome'
SELENIUM_DRIVER_EXECUTABLE_PATH = binary_path
SELENIUM_DRIVER_ARGUMENTS = ['--headless=new', 'user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36']

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15'
]

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

RETRY_TIMES = 15
RETRY_HTTP_CODES = [500, 503, 504, 400, 403, 404, 408, 429]
PROXY_MODE = 0

PROXY_LIST = pathlib.Path(__file__).parent.parent / pathlib.Path('jobs_scraper/proxy_list.txt')

RANDOMIZE_DOWNLOAD_DELAY = True
COOKIES_ENABLED = True
COOKIES_DEBUG = True

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'jobs_scraper.middlewares.UserAgentRotatorMiddleware': 200,
    # 'jobs_scraper.middlewares.CloudFlareMiddleware': 480,
    'scrapy_proxies.RandomProxy': 600,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 610,
    'scrapy_selenium.SeleniumMiddleware': 680,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': 690,
}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   # "jobs_scraper.pipelines.JsonWriterPipeline": 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True

# The initial download delay
AUTOTHROTTLE_START_DELAY = 2

# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 6

# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0

# Enable showing throttling stats for every response received:
AUTOTHROTTLE_DEBUG = False

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

# Feed
FEED_EXPORT_ENCODING = "utf-8"
FEED_URI_PARAMS = "jobs_scraper.utils.uri_params"
FEED_EXPORTERS = {"parquet": "zuinnote.scrapy.contrib.bigexporters.ParquetItemExporter"}

# TODO: Use Azure Datalake Gen2 container
FEEDS = {
   "/tmp/%(timestamp_now_filepath)s/%(timestamp_now_filename)s": {
      "format": "parquet",
      "encoding": "utf8",
      "store_empty": False,
      "item_export_kwargs": {
         "compression": "SNAPPY",  # compression to be used in Parquet, UNCOMPRESSED, GZIP, SNAPPY (package: python-snappy), LZO (package: lzo), BROTLI (package: brotli), LZ4 (package: lz4), ZSTD (package: zstandard) note: compression may require additional libraries
         "times": "int96",  # type for times int64 or int96, spark is int96 only
         "hasnulls": True,  # can contain nulls
         "convertallstrings": False,  # convert all values to string. recommended for compatibility reasons, conversion to native types is suggested as part of the ingestion in the processing platform
         "writeindex": False,  # write index as extra column
         "objectencoding": "infer",  # schema of data
         "rowgroupoffset": 50000000,  # offset row groups
         "items_rowgroup": 10000,  # how many items per rowgroup, should be several thousands, e.g. between 5,000 and 30,000. The more rows the higher the memory consumption and the better the compression on the final parquet file
      },
   }
}
