import scrapy


class ZillowParserSpider(scrapy.Spider):
    name = "zillow_parser"
    allowed_domains = ["www.zillow.com"]
    start_urls = ["https://www.zillow.com/"]

    def parse(self, response):
        pass
