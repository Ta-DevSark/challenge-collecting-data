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
    