

import os
import logging 
import time 

import scrapy
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains

class ApfCrawlerSpider(scrapy.Spider):
    name = "apf_crawler"
    allowed_domains = ["www.apartments.com"]

    def start_requests(self, housing_type="apartments"):
        city, state = 'austin', 'tx'
        url = f"https://www.apartments.com/{housing_type}/{city}-{state}/"
        yield SeleniumRequest(
            url=url,
            callback=self.parse,
            wait_time=10,
        )

    def parse(self, response):
       
        link_selector = 'article.placard a.property-link::attr(href)'
        links = response.css(link_selector).getall()

        # Since the same link may appear multiple times, use a set to remove duplicates
        unique_links = set(links)
        print(len(unique_links))
        for link in unique_links:
            # Process each unique link
            print(link) 

        next_page = response.css('.pagination a.next::attr(href)').get()
        if next_page:
            yield SeleniumRequest(
                url=next_page,
                callback=self.parse,
                wait_time=10,
                wait_until=EC.element_to_be_clickable((By.CLASS_NAME, next_page).click())
            )