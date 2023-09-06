from datetime import datetime
from uuid import uuid4

from scrapy import Spider


def uri_params(params: dict, spider: Spider) -> dict:
    now = datetime.now()
    file_type = "parquet"
    timestamp_now_fp = f"{now.year}/{now.month}/{now.day}/{now.hour}/{now.minute}"

    return {
        **params,
        "timestamp_now_filepath": f"bronze/{spider.name}/{timestamp_now_fp}",
        "timestamp_now_filename": f"{spider.name}-{uuid4()}-{timestamp_now_fp.replace('/', '')}.{file_type}"
    }
