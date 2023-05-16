import scrapy
import pandas as pd
class PropertySpider(scrapy.Spider):
    name = "property"
    allowed_domains = ["www.immoweb.be"]
    start_urls = ["https://www.immoweb.be/en/classified/house/for-sale/gent/9000/10567419"]

    def parse(self, response):
        
        
        yield pd.concat(pd.read_html(response.text)).set_index(0).T.to_dict(orient='records')[0]
       
      
