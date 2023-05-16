import scrapy
import pandas as pd

class ImmoSpider(scrapy.Spider):
    name = "scrapytest"
    start_urls = ['https://www.immoweb.be/en/search/house-and-apartment/for-sale?countries=BE&page=1&orderBy=relevance']

    def parse(self, response):
        for link in response.css('div.card--result__body a::attr(href)'):
            yield response.follow(link, callback=self.parse_house)
            # meta={'playwright' : True}
        for i in range (1, 2):
            next_page = f'https://www.immoweb.be/en/search/house-and-apartment/for-sale?countries=BE&page={i}&orderBy=relevance'
            yield response.follow(next_page, callback=self.parse)
            
    def parse_house(self, response):
        yield pd.concat(pd.read_html(response.body)).set_index(0).T.to_dict(orient='records')[0]