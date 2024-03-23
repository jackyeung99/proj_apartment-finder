import scrapy


class CityScraperSpider(scrapy.Spider):
    name = "city_scraper"
    allowed_domains = ["www.citydata.com"]
    start_urls = ["https://www.citydata.com"]

    def parse(self, response):
        pass
