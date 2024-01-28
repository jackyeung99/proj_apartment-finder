

import logging 
import re

import scrapy
from scrapy_selenium import SeleniumRequest
class apf_crawler_Spider(scrapy.Spider):
    
    name = "apf_crawler"
    allowed_domains = ["www.apartments.com"]

    def __init__(self, city='austin', state='tx', housing_type="apartments"):
        super(apf_crawler_Spider, self).__init__()
        # adjustable paramters
        self.housing_type = housing_type
        self.city = city
        self.state = state
        logging.info(f"Spider for {city}, {state} initialized")
        # storage
        self.page_num = 0
        self.list_of_apartment_links = []
        

    def start_requests(self):
        ''' Init scrapy framework'''
        initial_url = f"https://www.apartments.com/apartments/{self.city}-{self.state}/0/"
        logging.info(f"Starting requests at {initial_url}")
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
            logging.info(f"Found max page number: {max_page_num}")
            if max_page_num_match:
                max_page_num = int(max_page_num_match.group(1))
                return self.start_scraping(max_page_num)

    def start_scraping(self, max_page_num):
        '''scrapes all pages concurrently that's page number is below max'''
        logging.debug(f"Scraping page: {url}")
        for page_num in range(max_page_num+1):
            url = f"https://www.apartments.com/apartments/{self.city}-{self.state}/{page_num}/"
            yield SeleniumRequest(
                url=url,
                callback=self.parse,
                wait_time=10,
            )
        
    def parse(self, response):
        ''' Find all apartment links'''
        link_selector = 'article.placard a.property-link::attr(href)'
        unique_links = set(response.css(link_selector).getall())
        logging.info(f"Found {len(unique_links)} unique links on a page")
        self.list_of_apartment_links.extend(unique_links)

    def dump(self):
        '''export links into json'''
        file_path = f'data/apartments_link/{self.city}_{self.state}_apartment_links.json'
        with open(file_path, mode="w") as f:
            f.writelines([f"{line}\n" for line in self.list_of_apartment_links])
        logging.info(f"Dumped links to {file_path}")

    def closed(self, reason):
        # self.dump()
        print(f"Spider closed because {reason}")