# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
class ApfScraperLinkItem(scrapy.Item):
    PropertyUrl = scrapy.Field()

class ApartmentComplex(scrapy.Item):
    PropertyName = scrapy.Field()
    PropertyId = scrapy.Field()
    PropertyUrl = scrapy.Field()
    Lat = scrapy.Field()
    Long = scrapy.Field()
    Address = scrapy.Field()
    Neighborhood = scrapy.Field()
    PriceRange = scrapy.Field()
    ReviewScore = scrapy.Field()
    NumReviews = scrapy.Field()
    NumUnits = scrapy.Field()
    Details = scrapy.Field()
    
class ApartmentUnit(scrapy.Item):
    PropertyId = scrapy.Field()
    MaxRent = scrapy.Field()
    ModelName = scrapy.Field()
    Beds = scrapy.Field()
    Baths = scrapy.Field()
    SquareFootage = scrapy.Field()

class ComplexAmmenities(scrapy.Item):
    PropertyId = scrapy.Field()
    CommunityAmenities = scrapy.Field()

class UnitAmmenities(scrapy.Item):
    PropertyId = scrapy.Field()
    CommunityAmenities = scrapy.Field()

# class contact_info(scrapy.Item):
    
    