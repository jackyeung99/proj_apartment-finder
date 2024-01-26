

import logging 
import re

import scrapy
from scrapy_selenium import SeleniumRequest
class ApfCrawlerSpider(scrapy.Spider):
    
    name = "apf_crawler"
    allowed_domains = ["www.apartments.com"]

    def __init__(self, city='Austin', state='tx', housing_type="apartments"):
        super(ApfCrawlerSpider, self).__init__()
        # adjustable paramters
        self.housing_type = housing_type
        self.city = city
        self.state = state
        # storage
        self.page_num = 0
        self.list_of_apartment_links = []

    def start_requests(self):
        ''' Init scrapy framework'''
        initial_url = f"https://www.apartments.com/apartments/{self.city}-{self.state}/0/"
        yield SeleniumRequest(
            url=initial_url,
            callback=self.parse_initial,
            wait_time=10,
        )
        
    def parse_initial(self, response):
        ''' Finds the maximun page listed then initializes scraper'''
        page_range_text = response.css(".pageRange::text").get()
        if page_range_text:
            max_page_num_match = re.search(r'Page \d+ of (\d+)', page_range_text)
            if max_page_num_match:
                max_page_num = int(max_page_num_match.group(1))
                return self.start_scraping(max_page_num)

    def start_scraping(self, max_page_num):
        '''scrapes all pages below max concurrently '''
        for page_num in range(max_page_num+1):
            url = f"https://www.apartments.com/apartments/{self.city}-{self.state}/{page_num}/"
            yield SeleniumRequest(
                url=url,
                callback=self.parse,
                wait_time=10,
            )
        
    def parse(self, response):
        '''retrieve apartment links for page'''
        link_selector = 'article.placard a.property-link::attr(href)'
        unique_links = set(response.css(link_selector).getall())
        self.list_of_apartment_links.extend(unique_links)

    def dump(self):
        '''export links into json'''
        with open(f'{self.city}_{self.state}_apartment_links.json',mode="w") as f:
            f.writelines([f"{line}\n" for line in self.list_of_apartment_links])
        
    def closed(self, reason):
        self.dump()
        print(f"Spider closed because {reason}")