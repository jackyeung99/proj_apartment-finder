import scrapy

from scrapy_selenium import SeleniumRequest
from apf_scraper.items import ApfUnitItem, ApfGeneralInfoItem

import logging
import os
import json

from pympler import muppy, summary
from scrapy import signals

class apf_parser_Spider(scrapy.Spider):
    name = "apf_parser"
    custom_settings = {
        'ITEM_PIPELINES': {
            'apf_scraper.pipelines.ApartmentGeneralInfoPipeline': 100,
            'apf_scraper.pipelines.UnitPricesPipeline': 200,
        }
    }

    
    def __init__(self,city,state,*args, **kwargs):
        super(apf_parser_Spider, self).__init__(*args, **kwargs)
        self.city = city.lower()
        self.state = state.lower()
        # file handling
        self.base_dir = f"../data/{self.city}_{self.state}"  
        self.links_file = os.path.join(self.base_dir, f"{self.city}_{self.state}_links.txt") 
        self.links = self.get_links(self.links_file) 
        self.profile_memory()

    def get_links(self,links):
        logging.debug(os.getcwd())
        file_path = os.path.join(links)
        try:
            with open(file_path,mode="r") as f:
                links = [line.strip() for line in f if line.strip()]
                return links
            
        except FileNotFoundError as e:
            logging.critical(f'File not found: {file_path}')
            return []
        except json.JSONDecodeError:
            self.logger.error(f'Error decoding JSON from file: {file_path}')
            return []


    def start_requests(self):
        ''' Init scrapy framework'''
        for link in self.links:
            logging.debug(f'Accessing apartment at: {link}')
            yield SeleniumRequest(
                url=link,
                callback=self.parse,
                wait_time=10,
                
            )
    
    def parse_general_info(self, response):    
        info = {
            'property_name': response.css('#propertyName::text').get().strip(),
            'property_id':  response.css('body > div.mainWrapper > main::attr(data-listingid)').get(),
            'property_url': response.url,
            'address': response.css('#propertyAddressRow .delivery-address span::text').get(),
            'neighborhood_link': response.css('#propertyAddressRow .neighborhoodAddress a::attr(href)').get(),
            'neighborhood': response.css('#propertyAddressRow .neighborhoodAddress a::text').get(),
            'reviews': response.css('span.reviewRating ::text').get('None'),
            'verification': response.css('#tooltipToggle span::text').get('un-verified'),
        }
        return info

    def parse_unit_prices(self, response):
        # Improve data extraction and structure
        units = response.css('.unitContainer')
        apartment_id = response.css('body > div.mainWrapper > main::attr(data-listingid)').get()
        for unit in units:
            item = ApfUnitItem(
                PropertyId = apartment_id,
                MaxRent = unit.attrib.get('data-maxrent'),
                Model = unit.attrib.get('data-model'),
                Beds = unit.attrib.get('data-beds'),
                Baths =  unit.attrib.get('data-baths'),
                SquareFootage = unit.css('.sqftColumn span:nth-of-type(2)::text').get()
            )
            yield item

    def parse_amenities(self, response):
        amenities = set(response.css('li.specInfo span::text').getall())
        return list(amenities)

    def parse(self, response):
        general_info = self.parse_general_info(response)
        yield ApfGeneralInfoItem(
            PropertyName=general_info['property_name'],
            PropertyId = general_info['property_id'],
            PropertyUrl=general_info['property_url'],
            Address=general_info['address'],
            NeighborhoodLink=general_info['neighborhood_link'],
            Neighborhood=general_info['neighborhood'],
            ReviewScore=general_info['reviews'],
            VerifiedListing=general_info['verification'],
            Amenities=self.parse_amenities(response)
        )

        # Yield unit prices separately to keep the logic clear and maintainable
        yield from self.parse_unit_prices(response)

    def profile_memory(self):
        all_objects = muppy.get_objects()
        print(f"Total objects in memory: {len(all_objects)}")

        suml = summary.summarize(all_objects)
        summary.print_(suml)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(apf_parser_Spider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, reason):
        self.profile_memory()
        print(f"Spider closed because {reason}")