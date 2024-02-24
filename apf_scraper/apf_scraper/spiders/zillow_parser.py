from typing import Any
import scrapy
from scrapy.http import JsonRequest
from urllib.parse import urlparse, parse_qs, urlencode, urljoin
import json
import time 
import random

class ZillowParserSpider(scrapy.Spider):
    name = "zillow_parser"
    allowed_domains = ["www.zillow.com"]
    start_urls = ['https://www.zillow.com/homes/NY_rb/']
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
    
    # zpid: list[str], **kwargs

    def __init__(self):
        super().__init__()
        self.zpid = ['340066443', '341589101', '2053646109', '2053694999', '2064143172', '2057732979', '2055997847', '2053477066', '2098495358', '2083315848']

    def start_requests(self):
        fsbo_url = 'https://www.zillow.com/homes/fsbo/'
        yield scrapy.Request(fsbo_url, callback=self.start_main_requests)

    def start_main_requests(self, response):
        for start_url in self.start_urls:
            yield scrapy.Request(start_url, callback=self.send_requests)
    
    def send_requests(self,response):  
        for item in self.zpid:
            # zpid = result.get('zpid')
            query_id = '4c19ac196fd0f1e7e30ca7e7f9af85d5'
            operation_name = 'ForSaleDoubleScrollFullRenderQuery'

            url_params = {
                'zpid': item,
                'contactFormRenderParameter': '',
                'queryId': query_id,
                'operationName': operation_name,
            }
            
            json_payload = {
                'clientVersion' : "home-details/6.0.11.5970.master.8d248cb",
                'operationName' : operation_name,
                'queryId' : query_id,
                'variables' : {
                    'contactFormRenderParameter' : {
                        'isDoubleScroll' : True,
                        'platform' : 'desktop',
                        'zpid' : item,
                    },
                    'zpid' : item
                }
            }

            api_url = 'https://www.zillow.com/graphql/?' + urlencode(url_params)
            print(api_url)
            # yield scrapy.Request(
            #             url=api_url, 
            #             method='POST', 
            #             body=json.dumps(json_payload), 
            #             callback=self.parse_property_page_json
            #             )

    def parse_property_page_json(self, response):
        json_dict = json.loads(response.text)
        data_dict = json_dict.get('data', dict())
        property_dict = data_dict.get('property')
        if property_dict is None:
            return

        print(property_dict)
       