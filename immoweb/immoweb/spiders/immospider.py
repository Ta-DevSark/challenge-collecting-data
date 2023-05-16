
import scrapy


class Immospider(scrapy.Spider):
    name = "immospider"
    
    def start_requests(self):
       urls = ["https://www.immoweb.be/en/search/house-and-apartment/for-sale?countries=BE&page=1&orderBy=relevance",]
       
       for url in urls:
            yield scrapy.Request(url = url, callback = self.parse)
       
    def parse(self, response):
                
        links = response.css('h2 a::attr(href)').extract()

        for link in links:
            yield {
                    'link': link
            }
        
       
    

    

