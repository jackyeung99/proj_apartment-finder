import scrapy


class ApartmentParserSpider(scrapy.Spider):
    name = "apartment_parser"
    allowed_domains = ["www.apartments.com"]
    start_urls = ["https://www.apartments.com/"]

    def parse(self, response):
        pass
