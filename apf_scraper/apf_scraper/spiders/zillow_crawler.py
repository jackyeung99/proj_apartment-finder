import scrapy

import scrapy
import json
from scrapy.crawler import CrawlerProcess
import scrapy
from scrapy.http import JsonRequest
from urllib.parse import urlparse, parse_qs, urlencode, urljoin
import json
import js2xml
from parsel import Selector
import random

class ZillowCrawlerSpider(scrapy.Spider):
    name = "zillow_crawler"
    allowed_domains = ["zillow.com"]
    start_urls = [ 'https://www.zillow.com/homes/NY_rb/' ]
    custom_settings = {
            'DEFAULT_REQUEST_HEADERS': {
                'authority': 'www.zillow.com',
                'pragma': 'no-cache',
                'cache-control': 'no-cache',
                'sec-ch-ua': '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"macOS"',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en;q=0.9,en-US;q=0.8,lt;q=0.7',
                }
            }

    def __init__(self, start_urls=None):
        super().__init__()
        self.filters =  {
        "isForSaleForeclosure": {"value": False},
        "isMultiFamily": {"value": False},
        "isAllHomes": {"value": False},
        "isAuction": {"value": False},
        "isNewConstruction": {"value": False},
        "isForRent": {"value": True},
        "isLotLand": {"value": False},
        "isManufactured": {"value": False},
        "isForSaleByOwner": {"value": False},
        "isComingSoon": {"value": False},
        "isForSaleByAgent": {"value": False},
        "isApartment": {"value": True}
        }
        if start_urls is not None:
            self.start_urls = start_urls.split('|')

    def start_requests(self):
        fsbo_url = 'https://www.zillow.com/homes/fsbo/'
        yield scrapy.Request(fsbo_url, callback=self.start_main_requests)

    def start_main_requests(self, response):
        for start_url in self.start_urls:
            yield scrapy.Request(start_url, callback=self.parse_property_list_html)
    
    def parse_property_list_html(self, response):
        selector = Selector(response.text)
        script_data = json.loads(selector.css("script#__NEXT_DATA__::text").get())
        query_data = script_data["props"]["pageProps"]["searchPageState"]["queryState"]
        query_data["filterState"] = self.filters
        full_query = {
        "searchQueryState": query_data,
        "wants": {
            "cat1": ["mapResults"],
            "cat2": ["mapResults"]
            },
        "requestId": random.randint(2,10)
        }
        api_url = 'https://www.zillow.com/async-create-search-page-state'
        headers = {
            'content-type': 'application/json'
        }

        yield scrapy.Request(
            url=api_url, 
            callback=self.parse_property_list_json, 
            method='PUT', 
            body=json.dumps(full_query), 
            headers=headers
            )

    def parse_property_list_json(self, response):
        json_str = response.text
        json_dict = json.loads(json_str)
        print(len(json_dict['cat1']['searchResults']))
        first = json_dict['cat1']['searchResults']['mapResults']
        print(first[0])

        # print([(x.get('zpid',''),x.get('price','')) for x in first])
        

        
        

