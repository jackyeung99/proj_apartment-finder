
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

    def __init__(self, city='Austin', state='tx', housing_type="apartments"):
        super(ApfCrawlerSpider, self).__init__()
        logging.getLogger().setLevel(logging.WARNING)
        self.housing_type = housing_type
        self.city = city
        self.state = state
        self.page_num = 0
        self.list_of_apartment_links = []
        

    def start_requests(self):
        self.url = f"https://www.apartments.com/{self.housing_type}/{self.city}-{self.state}/{self.page_num}/"
        yield SeleniumRequest(
            url=self.url,
            callback=self.parse,
            wait_time=10,
        )

    def parse(self, response):
        link_selector = 'article.placard a.property-link::attr(href)'
        unique_links = set(response.css(link_selector).getall())

        for link in unique_links:
            self.list_of_apartment_links.append(link)

        next_page_selector = '.paging a.next'
        next_page_element = response.css(next_page_selector)

        if next_page_element:
            self.page_num += 1
            next_page_url = f"https://www.apartments.com/apartments/{self.city}-{self.state}/{self.page_num}/"
            yield SeleniumRequest(
                url=next_page_url,
                callback=self.parse,
                wait_time=10,
            )
        else:
            # dump links into file
            with open(f'{self.city}_{self.state}_apartment_links.json',mode="w") as f:
                f.writelines([f"{line}\n" for line in self.list_of_apartment_links])
            return