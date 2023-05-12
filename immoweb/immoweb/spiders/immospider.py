import scrapy


class ImmospiderSpider(scrapy.Spider):
    name = "immospider"
    allowed_domains = ["www.immoweb.be"]
    start_urls = ["https://www.immoweb.be/en/search/house-and-apartment/for-sale?countries=BE"]

    def parse(self, response):
        pass
