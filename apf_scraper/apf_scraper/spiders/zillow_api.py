from apf_scraper.creds import ZILLOW_API_HOST, ZILLOW_API_KEY
from apf_scraper.items import Apartment
import scrapy
import json 

class ZillowAPI(scrapy.Spider):
    name = 'zillow_api'
    allowed_domains = ['zillow56.p.rapidapi.com']
    
   
    def __init__(self, city, state,file, page_limit=2,):
        super().__init__()
        self.city = city
        self.state = state
        self.page_limit = page_limit
        self.file = file
        self.start_url = f'https://zillow56.p.rapidapi.com/search?location={city}, {state}'
        self.headers = {
        "X-RapidAPI-Key": ZILLOW_API_KEY,
        "X-RapidAPI-Host": ZILLOW_API_HOST  
        }
    
    def start_requests(self):
        for page in range(1,self.page_limit+1):
            url = self.start_url + f"&page={page}&status=forRent&isApartment=true&"
            yield scrapy.Request(url=self.start_url,
                                 headers=self.headers,
                                 callback=self.parse)
            break

    def parse(self, response):
        json_response = response.json()
        for unit in json_response: 
            if zpid in unit.keys():
                zpid = unit.get('zpid')
                url = "https://zillow56.p.rapidapi.com/property" + f"&zpid={zpid}"
                yield scrapy.Request(
                    url=url,
                    headers=self.headers,
                    callback=self.parse_property_page
                )


    def parse_property_page(self,response): 
        json_response = response.json()

        yield Apartment()
            
