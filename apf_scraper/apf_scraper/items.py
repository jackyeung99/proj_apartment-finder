# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class City(scrapy.Item):
    CityId = scrapy.Field()         #Primary Key 
    CityName = scrapy.Field()
    COL = scrapy.Field()
    Population = scrapy.Field()
    CrimeRate = scrapy.Field()
    TaxRate = scrapy.Field()
    Unemployment = scrapy.Field()
    MedianIncome = scrapy.Field()
    Growth = scrapy.Field()

class leasing_info(scrapy.Item):
    LeasingId = scrapy.Field()      #Primary Key
    Name = scrapy.Field()
    Phone = scrapy.Field()

class ApartmentComplex(scrapy.Item):
    ComplexId = scrapy.Field()      #Primary Key
    CityId = scrapy.Field()         #Foreign Key 
    Name = scrapy.Field()
    PropertyUrl = scrapy.Field()
    Lat = scrapy.Field()
    Long = scrapy.Field()
    PriceRange = scrapy.Field()
    Address = scrapy.Field()
    Neighborhood = scrapy.Field()
    ReviewScore = scrapy.Field()
    NumReviews = scrapy.Field()
    NumUnits = scrapy.Field()
    Details = scrapy.Field()
    
class ApartmentUnit(scrapy.Item):
    UnitId = scrapy.Field()         #Primary Key
    PropertyId = scrapy.Field()     #Foreign Key 
    MaxRent = scrapy.Field()
    ModelName = scrapy.Field()
    Beds = scrapy.Field()
    Baths = scrapy.Field()
    SquareFootage = scrapy.Field()

class ComplexAmmenities(scrapy.Item):
    PropertyId = scrapy.Field()     #Foreign Key 
    CommunityAmenities = scrapy.Field()

class UnitAmmenities(scrapy.Item):
    PropertyId = scrapy.Field()     #Foreign Key 
    CommunityAmenities = scrapy.Field()


    
    