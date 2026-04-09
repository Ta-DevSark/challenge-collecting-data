--- immoweb/immoweb/spiders/getalldata.py
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

+++ immoweb/immoweb/spiders/getalldata.py
"""
Spider for extracting detailed property data from Immoweb.be

This spider crawls property listings and extracts structured data
including price, location, features, and building characteristics.
"""

import re
import json
from typing import Optional, Dict, Any

from immoweb.items import ImmowebItem
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class GetalldataSpider(CrawlSpider):
    """Spider to extract all property data from Immoweb.be"""

    name = "getalldata"
    allowed_domains = ["www.immoweb.be"]

    # Generate start URLs for first 334 pages (adjust as needed)
    start_urls = [
        f"https://www.immoweb.be/en/search/house-and-apartment/for-sale?countries=BE&page={i}"
        for i in range(1, 335)
    ]

    custom_settings = {
        # Specify exported fields and their order
        'FEED_EXPORT_FIELDS': [
            "locality", "property_type", "subtype_property", "price",
            "type_of_sale", "number_of_rooms", "living_area",
            "kitchen_fully_equiped", "is_furnished", "has_open_fire",
            "has_terrace", "terrace_area", "has_garden", "garden_surface",
            "habitable_surface", "plot_land_surface", "number_of_facades",
            "has_swimming_pool", "building_state"
        ],
        # Respect robots.txt
        'ROBOTSTXT_OBEY': True,
        # Add delay between requests
        'DOWNLOAD_DELAY': 2,
        # Limit concurrent requests
        'CONCURRENT_REQUESTS_PER_DOMAIN': 8,
    }

    rules = (
        Rule(
            LinkExtractor(
                allow=('en/classified/(house|apartment)/for-sale/'),
                unique=True
            ),
            callback='parse_item',
            follow=True
        ),
    )

    @staticmethod
    def bool_to_yesno(value: Optional[bool]) -> str:
        """Convert boolean to Yes/No string."""
        if value is None:
            return "None"
        return "Yes" if value else "No"

    @staticmethod
    def is_hyper_kitchen(value: Optional[str]) -> str:
        """Check if kitchen type contains 'HYPER'."""
        if not value:
            return "None"
        return "Yes" if "HYPER" in value.upper() else "No"

    def parse_item(self, response: object) -> Dict[str, Any]:
        """
        Parse property details from the response.

        Args:
            response: Scrapy response object containing the page HTML

        Yields:
            ImmowebItem with extracted property data
        """
        # Extract JSON data from script tag
        classified_script = response.css('script:contains("window.classified")::text').get()

        if not classified_script:
            self.logger.warning(f"No classified data found for URL: {response.url}")
            return

        # Extract JSON from script content
        match = re.search(r'({.+})', classified_script)
        if not match:
            self.logger.warning(f"Could not parse JSON for URL: {response.url}")
            return

        json_dict = match.group(0)

        try:
            classified_dict = json.loads(json_dict)
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON decode error for URL {response.url}: {str(e)}")
            return

        property_key = classified_dict.get('property', {})
        price_key = classified_dict.get('price', {})
        transaction_key = classified_dict.get('transaction', {}).get('sale', {})

        # Initialize item
        item = ImmowebItem()

        # Extract basic properties
        item['locality'] = property_key.get('location', {}).get('locality')
        item['property_type'] = property_key.get('type')
        item['subtype_property'] = property_key.get('subtype')
        item['price'] = price_key.get('mainValue')
        item['type_of_sale'] = price_key.get('type')
        item['number_of_rooms'] = property_key.get('bedroomCount')
        item['is_furnished'] = self.bool_to_yesno(transaction_key.get('isFurnished'))
        item['has_open_fire'] = self.bool_to_yesno(property_key.get('fireplaceExists'))
        item['has_terrace'] = self.bool_to_yesno(property_key.get('hasTerrace'))
        item['terrace_area'] = property_key.get('terraceSurface')
        item['has_garden'] = self.bool_to_yesno(property_key.get('hasGarden'))
        item['garden_surface'] = property_key.get('gardenSurface')
        item['habitable_surface'] = property_key.get('netHabitableSurface')
        item['has_swimming_pool'] = self.bool_to_yesno(property_key.get('hasSwimmingPool'))

        # Extract nested properties with error handling
        try:
            item['living_area'] = property_key.get('livingRoom', {}).get('surface')
            item['kitchen_fully_equiped'] = self.is_hyper_kitchen(
                property_key.get('kitchen', {}).get('type')
            )
            item['plot_land_surface'] = property_key.get('land', {}).get('surface')
            item['number_of_facades'] = property_key.get('building', {}).get('facadeCount')
            item['building_state'] = property_key.get('building', {}).get('condition')
        except (TypeError, AttributeError) as e:
            self.logger.debug(f"Missing nested data for URL {response.url}: {str(e)}")
            item['living_area'] = None
            item['kitchen_fully_equiped'] = "None"
            item['plot_land_surface'] = None
            item['number_of_facades'] = None
            item['building_state'] = "None"

        yield item
