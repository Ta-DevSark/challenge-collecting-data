# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ImmowebItem(scrapy.Item):
    # define the fields for your item here like:
    locality = scrapy.Field()
    property_type = scrapy.Field()
    subtype_property = scrapy.Field()
    price = scrapy.Field()
    type_of_sale = scrapy.Field()
    number_of_rooms = scrapy.Field()
    living_area = scrapy.Field()
    kitchen_fully_equiped = scrapy.Field()
    is_furnished = scrapy.Field()
    has_open_fire = scrapy.Field()
    has_terrace = scrapy.Field()
    terrace_area = scrapy.Field()
    has_garden = scrapy.Field()
    garden_surface = scrapy.Field()
    habitable_surface = scrapy.Field()
    plot_land_surface = scrapy.Field()
    number_of_facades = scrapy.Field()
    has_swimming_pool = scrapy.Field()
    building_state = scrapy.Field() 
