--- immoweb/immoweb/spiders/getallurls.py
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

class GetallurlsSpider(CrawlSpider):
    name = "getallurls"
    allowed_domains = ["www.immoweb.be"]
    start_urls = ["https://www.immoweb.be/en/search/house-and-apartment/for-sale?countries=BE&page=%d" % i for i in range(1,334)]

    rules = (
        Rule(LinkExtractor(allow=('en/classified/(house|apartment)/for-sale/'), unique=True), callback='parse_item', follow=True),
    )

    def parse_item(self, response: object) -> dict:
      yield{
         'url': response.url
      }

+++ immoweb/immoweb/spiders/getallurls.py
"""
Spider for extracting property URLs from Immoweb.be

This spider crawls search result pages and extracts all property listing URLs.
"""

from typing import Dict, Any

from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class GetallurlsSpider(CrawlSpider):
    """Spider to extract all property URLs from Immoweb.be"""

    name = "getallurls"
    allowed_domains = ["www.immoweb.be"]

    # Generate start URLs for first 334 pages (adjust as needed)
    start_urls = [
        f"https://www.immoweb.be/en/search/house-and-apartment/for-sale?countries=BE&page={i}"
        for i in range(1, 335)
    ]

    custom_settings = {
        # Respect robots.txt
        'ROBOTSTXT_OBEY': True,
        # Add delay between requests
        'DOWNLOAD_DELAY': 2,
        # Limit concurrent requests
        'CONCURRENT_REQUESTS_PER_DOMAIN': 8,
    }

    rules = (
        Rule(
            LinkExtractor(
                allow=('en/classified/(house|apartment)/for-sale/'),
                unique=True
            ),
            callback='parse_item',
            follow=True
        ),
    )

    def parse_item(self, response: object) -> Dict[str, str]:
        """
        Extract URL from the response.

        Args:
            response: Scrapy response object containing the page HTML

        Yields:
            Dictionary with 'url' key containing the property URL
        """
        yield {
            'url': response.url,
            'source_page': response.request.headers.get('Referer', b'').decode('utf-8', errors='ignore')
        }
