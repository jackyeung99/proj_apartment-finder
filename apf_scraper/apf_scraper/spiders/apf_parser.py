# import scrapy
# # from scrapy import Request
# # # from scrapy_selenium import SeleniumRequest
# # # from apf_scraper.items import ApfUnitItem, ApfGeneralInfoItem

# import logging
# import os
# import json

# class apf_parser_Spider(scrapy.Spider):
#     name = "apf_parser"
#     custom_settings = {
#         'ITEM_PIPELINES': {
#             'apf_scraper.pipelines.ApartmentGeneralInfoPipeline': 100,
#             'apf_scraper.pipelines.UnitPricesPipeline': 200,
#         }
#     }

    
#     def __init__(self,city,state,*args, **kwargs):
#         super(apf_parser_Spider, self).__init__(*args, **kwargs)
#         self.city = city.lower()
#         self.state = state.lower()
#         # file handling
#         self.base_dir = f"../data/{self.city}_{self.state}"  
#         self.links_file = os.path.join(self.base_dir, f"{self.city}_{self.state}_links.txt") 
#         self.links = self.get_links(self.links_file) 
        

#     def get_links(self,links):
#         logging.debug(os.getcwd())
#         file_path = os.path.join(links)
#         try:
#             with open(file_path,mode="r") as f:
#                 links = [line.strip() for line in f if line.strip()]
#                 return links
            
#         except FileNotFoundError as e:
#             logging.critical(f'File not found: {file_path}')
#             return []
#         except json.JSONDecodeError:
#             self.logger.error(f'Error decoding JSON from file: {file_path}')
#             return []


#     def start_requests(self):
#         ''' Init scrapy framework'''
#         for link in self.links:
#             logging.debug(f'Accessing apartment at: {link}')
#             yield SeleniumRequest(
#                 url=link,
#                 callback=self.parse,
#                 wait_time=10,
                
#             )
    
#     def parse_general_info(self, response):    
#         info = {
#             'property_name': response.css('#propertyName::text').get().strip(),
#             'property_id':  response.css('body > div.mainWrapper > main::attr(data-listingid)').get(),
#             'property_url': response.url,
#             'address': response.css('#propertyAddressRow .delivery-address span::text').get(),
#             'neighborhood_link': response.css('#propertyAddressRow .neighborhoodAddress a::attr(href)').get(),
#             'neighborhood': response.css('#propertyAddressRow .neighborhoodAddress a::text').get(),
#             'reviews': response.css('span.reviewRating ::text').get('None'),
#             'verification': response.css('#tooltipToggle span::text').get('un-verified'),
#         }
#         return info

#     def parse_unit_prices(self, response):
#         # Improve data extraction and structure
#         units = response.css('.unitContainer')
#         apartment_id = response.css('body > div.mainWrapper > main::attr(data-listingid)').get()
#         unique_apartments = set()
#         for unit in units:
#             # Extracting details for the unique check
#             model = unit.attrib.get('data-model')
#             max_rent = unit.attrib.get('data-maxrent')
#             beds = unit.attrib.get('data-beds')
#             baths = unit.attrib.get('data-baths')
#             square_footage = unit.css('.sqftColumn span:nth-of-type(2)::text').get()

#             # Creating a unique tuple to represent each unit
#             unique_identifier = (apartment_id, max_rent, model, beds, baths, square_footage)

#             # Check if the unit has already been processed
#             if unique_identifier not in unique_apartments:
#                 unique_apartments.add(unique_identifier)  # Add unique identifier to the set

#                 item = ApfUnitItem(
#                     PropertyId=apartment_id,
#                     MaxRent=max_rent,
#                     Model=model,
#                     Beds=beds,
#                     Baths=baths,
#                     SquareFootage=square_footage
#                 )
#                 yield item

#     def parse_amenities(self, response):
#         amenities = set(response.css('li.specInfo span::text').getall())
#         return list(amenities)

#     def parse(self, response):
#         general_info = self.parse_general_info(response)
#         yield ApfGeneralInfoItem(
#             PropertyName=general_info['property_name'],
#             PropertyId = general_info['property_id'],
#             PropertyUrl=general_info['property_url'],
#             Address=general_info['address'],
#             NeighborhoodLink=general_info['neighborhood_link'],
#             Neighborhood=general_info['neighborhood'],
#             ReviewScore=general_info['reviews'],
#             VerifiedListing=general_info['verification'],
#             Amenities=self.parse_amenities(response)
#         )

#         # Yield unit prices separately to keep the logic clear and maintainable
#         yield from self.parse_unit_prices(response)

#         self.log_live_references()

#     def log_live_references(self):
#         # Log the count of live HtmlResponse and Request objects
#         response_count = len(live_refs['HtmlResponse'])
#         request_count = len(live_refs['Request'])
#         self.logger.info(f"Live HtmlResponse objects: {response_count}")
#         self.logger.info(f"Live Request objects: {request_count}")

#     def spider_closed(self, reason):
#         print(f"Spider closed because {reason}")


import scrapy
from scrapy import Request
import logging
import os
import json
from apf_scraper.items import ApfUnitItem, ApfGeneralInfoItem

class ApfParserSpider(scrapy.Spider):
    name = "apf_parser"
    custom_settings = {
        'ITEM_PIPELINES': {
            'apf_scraper.pipelines.ApartmentGeneralInfoPipeline': 100,
            'apf_scraper.pipelines.UnitPricesPipeline': 200,
        },
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler': 500,
        },
        'PLAYWRIGHT_BROWSER_TYPE': 'chromium',
        'PLAYWRIGHT_LAUNCH_OPTIONS': {
            'headless': True,
        },
        'DOWNLOAD_TIMEOUT': 30,
    }

    def __init__(self, city, state, *args, **kwargs):
        super(ApfParserSpider, self).__init__(*args, **kwargs)
        self.city = city.lower()
        self.state = state.lower()
        self.base_dir = f"../data/{self.city}_{self.state}"
        self.links_file = os.path.join(self.base_dir, f"{self.city}_{self.state}_links.txt")
        self.links = self.get_links(self.links_file)

    def get_links(self, links_file):
        try:
            with open(links_file, mode="r") as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError as e:
            logging.critical(f'File not found: {links_file}')
            return []
        except json.JSONDecodeError:
            logging.error(f'Error decoding JSON from file: {links_file}')
            return []

    def start_requests(self):
        for link in self.links:
            yield Request(
                url=link,
                callback=self.parse,
                meta={
                    'playwright': True,
                    'playwright_include_page': True,
                    'playwright_page_coroutines': [
                        {'fn': 'wait_for_selector', 'selector': 'body'}
                    ]
                }
            )

    async def parse(self, response):
        page = response.meta['playwright_page']
        general_info = await self.parse_general_info(page)
        yield ApfGeneralInfoItem(**general_info)
        await self.parse_unit_prices(page, general_info['property_id'])
        await page.close()

    async def parse_general_info(self, page):
        property_name = await page.text_content('#propertyName')
        property_id = await page.evaluate('''() => document.querySelector('body > div.mainWrapper > main').getAttribute('data-listingid')''')
        property_url = page.url
        address = await page.text_content('#propertyAddressRow .delivery-address span')
        neighborhood_link = await page.get_attribute('#propertyAddressRow .neighborhoodAddress a', 'href')
        neighborhood = await page.text_content('#propertyAddressRow .neighborhoodAddress a')
        reviews = await page.text_content('span.reviewRating')
        verification = await page.text_content('#tooltipToggle span')
        
        return {
            'property_name': property_name,
            'property_id': property_id,
            'property_url': property_url,
            'address': address,
            'neighborhood_link': neighborhood_link,
            'neighborhood': neighborhood,
            'reviews': reviews,
            'verification': verification,
        }

    async def parse_unit_prices(self, page, property_id):
        units = await page.query_selector_all('.unitContainer')
        unique_apartments = set()
        for unit in units:
            model = await unit.get_attribute('data-model')
            max_rent = await unit.get_attribute('data-maxrent')
            beds = await unit.get_attribute('data-beds')
            baths = await unit.get_attribute('data-baths')
            square_footage = await unit.text_content('.sqftColumn span:nth-of-type(2)')
            unique_identifier = (property_id, max_rent, model, beds, baths, square_footage)

            if unique_identifier not in unique_apartments:
                unique_apartments.add(unique_identifier)
                item = ApfUnitItem(
                    PropertyId=property_id,
                    MaxRent=max_rent,
                    Model=model,
                    Beds=beds,
                    Baths=baths,
                    SquareFootage=square_footage
                )
                yield item