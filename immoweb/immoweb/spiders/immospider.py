
import scrapy

class Immospider(scrapy.Spider):
    name = "immospider"
    def start_requests(self):
       yield scrapy.Request("https://www.immoweb.be/en/search/house-and-apartment/for-sale?countries=BE", 
                            meta={'playwright' : True})


    def parse(self, response):
       
        properties = response.css('article.card.card--result.card--xl')

        for property in properties:
            yield {
                    'url': property.css('h2 a').attrib['href']
            }
