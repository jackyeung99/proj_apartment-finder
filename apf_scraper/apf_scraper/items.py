# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
class ApfScraperLinkItem(scrapy.Item):
    PropertyUrl = scrapy.Field()

class ApfGeneralInfoItem(scrapy.Item):
    PropertyName = scrapy.Field()
    PropertyId = scrapy.Field()
    PropertyUrl = scrapy.Field()
    Address = scrapy.Field()
    NeighborhoodLink = scrapy.Field()
    Neighborhood = scrapy.Field()
    ReviewScore = scrapy.Field()
    VerifiedListing = scrapy.Field()
    Amenities = scrapy.Field()
    is_single_unit = scrapy.Field()

class ApfUnitItem(scrapy.Item):
    PropertyId = scrapy.Field()
    MaxRent = scrapy.Field()
    Model = scrapy.Field()
    Beds = scrapy.Field()
    Baths = scrapy.Field()
    SquareFootage = scrapy.Field()