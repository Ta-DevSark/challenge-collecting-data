"""import scrapy


class ImmospiderSpider(scrapy.Spider):
    name = "immospider"
    allowed_domains = ["www.immoweb.be"]
    start_urls = ["https://www.immoweb.be/en/search/house-and-apartment/for-sale?countries=BE"]

    def parse(self, response):
        pass
        """
import scrapy

class ImmospiderSpider(scrapy.Spider):
    name = "immospider"
    # allowed_domains = ["www.immoweb.be"]
    # start_urls = ["https://www.immoweb.be/en/search/house-and-apartment/for-sale?countries=BE"]
     #property_url = "https://www.immoweb.be/en/classified/apartment/for-sale/deinze/9800/10560242"

    def start_requests(self):
       yield scrapy.Request("https://www.immoweb.be/en/search/house-and-apartment/for-sale?countries=BE", 
                            meta={'playwright' : True})


    def parse(self, response):
        yield{
            'text' : response.text
        }
