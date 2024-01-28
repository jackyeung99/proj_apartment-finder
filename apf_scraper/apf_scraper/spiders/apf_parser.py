import scrapy
from scrapy_selenium import SeleniumRequest
from apf_scraper.items import ApfScraperItem
import logging
import os


class apf_parser_Spider(scrapy.Spider):
    name = "apf_parser"
    custom_settings = {
        'ITEM_PIPELINES': {
            'apf_scraper.pipelines.ApfScraperPipeline': 300,
        }
    }
    
    def __init__(self,city,state,*args, **kwargs):
        super(apf_parser_Spider, self).__init__(*args, **kwargs)
        self.city = city.lower()
        self.state = state.lower()
        # file handling
        self.base_dir = f"../data/{self.city}_{self.state}"  
        self.links_file = os.path.join(self.base_dir, f"{self.city}_{self.state}_links.txt") 
        self.output_file_path = os.path.join(self.base_dir, f"{self.city}_{self.state}.json")  
        self.links = self.get_links(self.links_file)
        

    def get_links(self,links):
        logging.debug(os.getcwd())
        file_path = os.path.join(links)
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
        for link in self.links:
            logging.debug(f'Accessing apartment at: {link}')
            yield SeleniumRequest(
                url=link,
                callback=self.parse,
                wait_time=10,
            )
    
    def parse_general_info(self,response):
        ''' Retrive information about the apartment complex'''
        property_name = response.css('#propertyName::text').get(default='').strip()
        property_url = response.url
        address = response.css('#propertyAddressRow > div > h2 > span.delivery-address > span::text').get(default='')
        neighborhood_link = response.css('#propertyAddressRow > div > h2 > span.neighborhoodAddress > a::attr(href)').get(default='')
        neighborhood = response.css('#propertyAddressRow > div > h2 > span.neighborhoodAddress > a::text').get(default='')
        reviews = response.css('span.reviewRating ::text').get(default='None')
        verification = response.css('#tooltipToggle > span:nth-child(1) > span::text').get(default='un-verified')
        gen_info_tuples = (property_name,property_url,address,neighborhood_link,neighborhood,reviews,verification)
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
        gen_info = self.parse_general_info(response)
        item = ApfScraperItem()
        item['PropertyName'] = gen_info[0]
        item['PropertyUrl'] = gen_info[1]
        item['Address'] = gen_info[2]
        item['NeighborhoodLink'] = gen_info[3]
        item['Neighborhood'] = gen_info[4]
        item['ReviewScore'] = gen_info[5]
        item['VerifiedListing'] = gen_info[6]
        item['Units'] = [dict(zip(["MaxRent", "Model", "Beds", "Baths", "SquareFootage"], unit)) for unit in self.parse_unit_prices(response)]
        item['Amenities'] = list(self.parse_ammenities(response))

        yield item