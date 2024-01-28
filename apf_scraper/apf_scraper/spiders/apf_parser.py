import scrapy
from scrapy_selenium import SeleniumRequest
import logging
import os


class apf_parser_Spider(scrapy.Spider):
    name = "apf_parser"

    def __init__(self,file_name):
        super(apf_parser_Spider, self).__init__()
        self.links = self.get_links(file_name)

    def get_links(self,file_name):
        logging.debug(os.getcwd())
        file_path = os.path.join("../","data", "apartments_links", file_name)
        try:
            with open(file_path,mode="r") as f:
                links = [line.strip() for line in f]
                logging.info(f'{len(links)} links have been loaded for scraping')
                return links
        except FileNotFoundError as e:
            logging.critical(f'File not found: {file_path}')
            return []


    def start_requests(self):
        ''' Init scrapy framework'''
        for link in self.links[:15]:
            logging.debug(f'Accessing apartment at: {link}')
            yield SeleniumRequest(
                url=link,
                callback=self.parse,
                wait_time=10,
            )
    
    def parse_general_info(self,response):
        ''' Retrive information about the apartment complex'''
        property_name = response.css('#propertyName::text').get(default='').strip()
        address = response.css('#propertyAddressRow > div > h2 > span.delivery-address > span::text').get(default='')
        neighborhood_link = response.css('#propertyAddressRow > div > h2 > span.neighborhoodAddress > a::attr(href)').get(default='')
        neighborhood = response.css('#propertyAddressRow > div > h2 > span.neighborhoodAddress > a::text').get(default='')
        reviews = response.css('span.reviewRating ::text').get(default='')
        verification = response.css('#tooltipToggle > span:nth-child(1) > span::text').get(default='un-verified')
        gen_info_tuples = (property_name,address,neighborhood_link,neighborhood,reviews,verification)
        return gen_info_tuples

    def parse_unit_prices(self,response):
        ''' Retrieve information for all units'''
        max_rent = response.css('.unitContainer::attr(data-maxrent)').getall()
        models = response.css('.unitContainer::attr(data-model)').getall()
        beds = response.css('.unitContainer::attr(data-beds)').getall()
        baths = response.css('.unitContainer::attr(data-baths)').getall()
        sq_foot = response.css('.sqftColumn span:nth-of-type(2)::text').getall()
        data_tuples = list(zip(max_rent, models, beds, baths,sq_foot))
        return data_tuples
    
    def parse_ammenities(self,response):
        '''Retriev information for all ammenities'''
        amenities_selector = 'li.specInfo span::text'
        amenities = set(response.css(amenities_selector).getall())  
        return amenities

    def parse(self, response):
        print("======== gen_info ===========")
        print(self.parse_general_info(response))
        print("======== gen_units ===========")
        print(self.parse_unit_prices(response))
        print("======== ammenities ===========")
        print(self.parse_ammenities(response))
