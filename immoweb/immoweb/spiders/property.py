import scrapy
import chompjs


class PropertySpider(scrapy.Spider):
    name = "property"
    allowed_domains = ["www.immoweb.be"]
    start_urls = ["https://www.immoweb.be/en/classified/house/for-sale/gent/9000/10567419"]

    def parse(self, response):
        
        script_text = response.css('script:contains("window.dataLayer")::text')
        
        json_data = chompjs.parse_js_object(script_text)
        
       
        pass
