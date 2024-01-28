# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ApfScraperItem(scrapy.Item):
    PropertyName = scrapy.Field()
    PropertyUrl = scrapy.Field()
    Address = scrapy.Field()
    NeighborhoodLink = scrapy.Field()
    Neighborhood = scrapy.Field()
    ReviewScore = scrapy.Field()
    VerifiedListing = scrapy.Field()
    Units = scrapy.Field() 
    Amenities = scrapy.Field()
