from typing import Iterable
import scrapy
from scrapy.http import Request
from scrapy_selenium import SeleniumRequest
from scrapy.selector import Selector

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from apf_scraper.items import ApfScraperItem
import os

class ApfCrawlerSpider(scrapy.Spider):
    name = "apf_crawler"
    allowed_domains = ["www.apartments.com"]

    def __init__(self, city='austin', state='tx', *args, **kwargs):
        super(ApfCrawlerSpider, self).__init__(*args, **kwargs)
        self.start_urls = [f"https://www.apartments.com/{city}-{state}/"]

        # Selenium setup
        opts = Options()
        opts.add_argument('--no-sandbox')
        opts.add_argument('--disable-gpu')
        opts.add_argument('--headless')  # Uncomment for headless mode
        if os.name == 'posix':
            opts.add_argument('--remote-debugging-port=9222')
            opts.add_argument('--disable-dev-shm-using')
        
        # Assuming chromedriver is one file up from the current script
        driver_path = os.path.join(os.path.dirname(__file__), '..', 'chromedriver')
        self.driver = webdriver.Chrome(options=opts)

    def start_requests(self):
        # Assuming you are scraping a city and state
        city = 'austin'
        state = 'tx'
        url = f"https://www.apartments.com/{city}-{state}/"
        yield SeleniumRequest(
            url=url, 
            callback=self.parse, 
            wait_time=10,
            # Update the wait condition based on the specific element you are waiting for
            wait_until=EC.element_to_be_clickable((By.CLASS_NAME, 'property-link'))
        )
            
    # def parse_apartment(self, response):
    def parse(self, response):
        # Find all apartment links on the page
        apartment_links = response.selector.css('.placardContainer .placard a::attr(href)').getall()
        
        # Yield a new request for each link
        for link in apartment_links:
            yield scrapy.Request(url=link, callback=self.parse_apartment)

        # Extract and follow pagination links
        next_page = response.css('.pagination a.next::attr(href)').get()
        if next_page is not None:
            yield SeleniumRequest(
                url=next_page, 
                callback=self.parse,
                wait_time=10,
                wait_until=EC.element_to_be_clickable((By.CLASS_NAME, 'property-link'))
            )

    def closed(self, reason):
        self.driver.quit()