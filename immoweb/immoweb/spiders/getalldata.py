import re
import json
from immoweb.items import ImmowebItem
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

class GetalldataSpider(CrawlSpider):
    name = "getalldata"
    allowed_domains = ["www.immoweb.be"]
    start_urls =  ["https://www.immoweb.be/en/search/house-and-apartment/for-sale?countries=BE&page=%d" % i for i in range(1,334)]

    custom_settings = {
    # Specify exported fields and their order
    'FEED_EXPORT_FIELDS': ["locality", "property_type", "subtype_property", "price", "type_of_sale", "number_of_rooms",
                           "living_area", "kitchen_fully_equiped", "is_furnished", "has_open_fire", "has_terrace",
                           "terrace_area", "has_garden", "garden_surface", "habitable_surface", "plot_land_surface",
                           "number_of_facades", "has_swimming_pool", "building_state"],
    }
    
    rules = (
        Rule(LinkExtractor(allow=('en/classified/(house|apartment)/for-sale/'), unique=True), callback='parse_item', follow=True),
    )

    def parse_item(self, response: object) -> dict:
        
        def bool_to_yesno(boolean: bool) -> str:
            if boolean:
                return "Yes"
            return "No"  
        
        def is_hyper_kitchen(value: str) -> str:
            if "HYPER" in value:
                return "Yes"
            return "No"        
              
        # Get json dictionary from html script tag        
        classified_script = response.css('script:contains("window.classified")::text').get()
        json_dict = re.search('({.+})', classified_script).group(0)
        classified_dict = json.loads(json_dict)
        property_key =classified_dict['property']
        price_key = classified_dict['price']
        
        # Generate item dictionary
        item = ImmowebItem()
        item['locality'] = property_key['location']['locality']
        item['property_type'] = property_key['type'] 
        item['subtype_property'] = property_key['subtype']
        item['price'] = price_key['mainValue']
        item['type_of_sale'] = price_key['type']
        item['number_of_rooms'] = property_key['bedroomCount']
        item['is_furnished'] = bool_to_yesno(classified_dict['transaction']['sale']['isFurnished'])
        item['has_open_fire'] = bool_to_yesno(property_key['fireplaceExists'])
        item['has_terrace'] = bool_to_yesno(property_key['hasTerrace'])
        item['terrace_area'] = property_key['terraceSurface']
        item['has_garden'] = bool_to_yesno(property_key['hasGarden'])
        item['garden_surface'] = property_key['gardenSurface']
        item['habitable_surface'] = property_key['netHabitableSurface']
        item['has_swimming_pool'] = bool_to_yesno(property_key['hasSwimmingPool'])
        try:
            item['living_area'] = property_key['livingRoom']['surface']
            item['kitchen_fully_equiped'] = is_hyper_kitchen(property_key['kitchen']['type'])
            item['plot_land_surface'] = property_key['land']['surface']
            item['number_of_facades'] = property_key['building']['facadeCount']
            item['building_state'] = property_key['building']['condition']
        except TypeError:
            item['living_area'] = None 
            item['kitchen_fully_equiped'] = "None"  
            item['plot_land_surface'] = None 
            item['number_of_facades'] = None   
            item['building_state'] = "None"
        yield item


        
