# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import logging

from scrapy import signals

# useful for handling different item types with a single interface
from scrapy.http.response.html import HtmlResponse
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
import cloudscraper
import numpy as np


class UserAgentRotatorMiddleware(UserAgentMiddleware):
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15'
    ]

    def __init__(self, user_agent=''):
        self.user_agent = user_agent

    def process_request(self, request, spider):
        rand_agent_index = np.random.randint(len(self.user_agents))
        self.user_agent = self.user_agents[rand_agent_index]
        request.headers.setdefault('User-Agent', self.user_agent)


class CloudFlareMiddleware:

    @staticmethod
    def is_cloudflare_challenged(response: HtmlResponse):
        blocker_selectors = response.xpath("//span[@id='challenge-error-text']//text()").extract()
        return len(blocker_selectors) > 0

    def process_response(self, request, response, spider):
        """Handles Scrapy response"""

        if not self.is_cloudflare_challenged(response=response):
            return response

        logger = logging.getLogger('cloudflaremiddleware')

        logger.debug(f"Cloudflare protection detected on {response.url}, trying to bypass...")

        scraper = cloudscraper.create_scraper()
        response = scraper.get(url=response.url)

        logger.debug(f'Successfully bypassed the protection for {response.url}')

        return HtmlResponse(url=response.url, body=response.text, encoding="utf-8")
