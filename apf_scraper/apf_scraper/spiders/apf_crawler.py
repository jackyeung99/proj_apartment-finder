

import logging 
import re
import os 
import json

import scrapy
from scrapy_selenium import SeleniumRequest
from apf_scraper.items import ApfScraperLinkItem

class apf_crawler_Spider(scrapy.Spider):
    
    custom_settings = {
        'ITEM_PIPELINES': {
            'apf_scraper.pipelines.LinkPipeline': 300,
        }
    }

    name = "apf_crawler"
    allowed_domains = ["www.apartments.com"]

    def __init__(self, city='austin', state='tx', housing_type="apartments",*args, **kwargs):
        super(apf_crawler_Spider, self).__init__(*args, **kwargs)
        self.city = city.lower()
        self.state = state.lower()
        self.housing_type = housing_type.lower()

    def start_requests(self):
        '''Start workflow for link crawler'''
        initial_url = f"https://www.apartments.com/{self.housing_type}/{self.city}-{self.state}/"
        yield SeleniumRequest(url=initial_url, callback=self.parse_initial, wait_time=10)

    def parse_initial(self, response):
        ''' pagination logic to scrape through all available pages'''
        max_page_num = self.extract_max_page(response)
        if max_page_num:
            for page_num in range(max_page_num + 1):
                url = f"https://www.apartments.com/{self.housing_type}/{self.city}-{self.state}/{page_num}/"
                yield SeleniumRequest(url=url, callback=self.parse, wait_time=10)
        
    def extract_max_page(self, response):
        '''Retrieve max page to limit pagination'''
        page_range_text = response.css(".pageRange::text").get()
        if page_range_text:
            return int(re.search(r'Page \d+ of (\d+)', page_range_text).group(1))
        return 0
  
    def parse(self, response):
        ''' Retrieve all unique apartment links'''
        link_selector = 'article.placard a.property-link::attr(href)'
        links = set(response.css(link_selector).getall())
        for link in links:
            yield ApfScraperLinkItem(PropertyUrl=link)

    def closed(self, reason):
        print(f"Spider closed because {reason}")