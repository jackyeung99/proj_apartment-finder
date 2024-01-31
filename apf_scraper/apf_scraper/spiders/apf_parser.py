import scrapy
from scrapy_selenium import SeleniumRequest
from apf_scraper.items import ApfUnitItem, ApfGeneralInfoItem

from scrapy.utils.trackref import get_oldest, iter_all
from scrapy.utils.trackref import live_refs
import logging
import os
import json

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
        unique_apartments = set()
        for unit in units:
            # Extracting details for the unique check
            model = unit.attrib.get('data-model')
            beds = unit.attrib.get('data-beds')
            baths = unit.attrib.get('data-baths')
            square_footage = unit.css('.sqftColumn span:nth-of-type(2)::text').get()

            # Creating a unique tuple to represent each unit
            unique_identifier = (model, beds, baths, square_footage)

            # Check if the unit has already been processed
            if unique_identifier not in unique_apartments:
                unique_apartments.add(unique_identifier)  # Add unique identifier to the set

                item = ApfUnitItem(
                    PropertyId=apartment_id,
                    MaxRent=unit.attrib.get('data-maxrent'),
                    Model=model,
                    Beds=beds,
                    Baths=baths,
                    SquareFootage=square_footage
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

        self.log_live_references()

    def log_live_references(self):
        # Log the count of live HtmlResponse and Request objects
        response_count = len(live_refs['HtmlResponse'])
        request_count = len(live_refs['Request'])
        self.logger.info(f"Live HtmlResponse objects: {response_count}")
        self.logger.info(f"Live Request objects: {request_count}")

    def spider_closed(self, reason):
        print(f"Spider closed because {reason}")