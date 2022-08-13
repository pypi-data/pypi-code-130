import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import MapCompose


class FirmItem(scrapy.Item):
    category = scrapy.Field()
    subcategory = scrapy.Field()
    name = scrapy.Field()
    website_link = scrapy.Field()
    location = scrapy.Field()
    min_project_size = scrapy.Field()
    avg_hourly_rate = scrapy.Field()
    rating = scrapy.Field()
    reviews = scrapy.Field()


class FirmLoader(ItemLoader):
    default_input_processor = MapCompose(str.strip)
