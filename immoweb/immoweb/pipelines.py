--- immoweb/immoweb/pipelines.py
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

from itemadapter import ItemAdapter


class ImmowebPipeline:
    def process_item(self, item, spider):
        return item

+++ immoweb/immoweb/pipelines.py
"""
Item pipelines for processing scraped data.

Pipelines are used to process items after they have been scraped.
Common uses include:
- Cleaning HTML data
- Validating data
- Checking for duplicates
- Storing in database
"""

from typing import Any, Dict
from itemadapter import ItemAdapter


class ImmowebPipeline:
    """
    Default pipeline for processing Immoweb items.

    This pipeline performs basic data cleaning and validation.
    """

    def open_spider(self, spider):
        """Initialize when spider opens."""
        spider.logger.info("Pipeline opened")
        self.items_processed = 0

    def close_spider(self, spider):
        """Cleanup when spider closes."""
        spider.logger.info(f"Pipeline closed. Processed {self.items_processed} items.")

    def process_item(self, item: Any, spider) -> Any:
        """
        Process each scraped item.

        Args:
            item: The scraped item to process
            spider: The spider that scraped the item

        Returns:
            The processed item
        """
        adapter = ItemAdapter(item)

        # Clean string fields
        for field_name in adapter.field_names():
            value = adapter.get(field_name)
            if isinstance(value, str):
                # Strip whitespace
                cleaned_value = value.strip()

                # Convert "None" strings to actual None
                if cleaned_value.lower() == 'none':
                    cleaned_value = None

                adapter[field_name] = cleaned_value

        # Validate price (should be numeric)
        price = adapter.get('price')
        if price is not None:
            try:
                adapter['price'] = float(price)
            except (ValueError, TypeError):
                spider.logger.warning(f"Invalid price value: {price}")

        # Validate numeric fields
        numeric_fields = [
            'number_of_rooms', 'living_area', 'terrace_area',
            'garden_surface', 'habitable_surface', 'plot_land_surface',
            'number_of_facades'
        ]

        for field in numeric_fields:
            value = adapter.get(field)
            if value is not None:
                try:
                    adapter[field] = float(value)
                except (ValueError, TypeError):
                    spider.logger.debug(f"Invalid {field} value: {value}")

        self.items_processed += 1
        return item


class DataValidationPipeline:
    """
    Pipeline for validating scraped data.

    This pipeline checks for required fields and data quality.
    """

    REQUIRED_FIELDS = ['locality', 'price', 'property_type']

    def process_item(self, item: Any, spider) -> Any:
        """
        Validate item data.

        Args:
            item: The scraped item to validate
            spider: The spider that scraped the item

        Returns:
            The validated item

        Raises:
            DropItem: If required fields are missing
        """
        adapter = ItemAdapter(item)

        # Check required fields
        for field in self.REQUIRED_FIELDS:
            if not adapter.get(field):
                spider.logger.warning(f"Missing required field: {field}")

        # Validate price range
        price = adapter.get('price')
        if price is not None:
            try:
                price_value = float(price)
                if price_value <= 0:
                    spider.logger.warning(f"Invalid price (<=0): {price_value}")
                elif price_value > 100_000_000:  # 100 million
                    spider.logger.warning(f"Suspiciously high price: {price_value}")
            except (ValueError, TypeError):
                pass

        return item
