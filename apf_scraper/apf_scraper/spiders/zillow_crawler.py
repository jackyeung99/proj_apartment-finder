
import scrapy
import json
import random
from pprint import pprint
from parsel import Selector
from apf_scraper.creds import PROXY

class ZillowCrawlerSpider(scrapy.Spider):
    name = "zillow_crawler"
    allowed_domains = ["zillow.com"]
    custom_settings = {
            'DEFAULT_REQUEST_HEADERS': {
                'authority': 'www.zillow.com',
                'pragma': 'no-cache',
                'cache-control': 'no-cache',
                'content-type': 'application/json',
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

    def __init__(self,city,state):
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
        self.start_url = f"https://www.zillow.com/{city}-{state}/rentals/"

    def start_requests(self):
        fsbo_url = r'https://www.zillow.com/new-york-ny/rentals/?searchQueryState=%7B%22pagination%22%3A%7B%7D%2C%22isMapVisible%22%3Atrue%2C%22mapBounds%22%3A%7B%22west%22%3A-74.43424032617187%2C%22east%22%3A-73.52512167382812%2C%22south%22%3A40.38633696547364%2C%22north%22%3A41.007916244996316%7D%2C%22usersSearchTerm%22%3A%22New%20York%20NY%22%2C%22regionSelection%22%3A%5B%7B%22regionId%22%3A6181%2C%22regionType%22%3A6%7D%5D%2C%22filterState%22%3A%7B%22fr%22%3A%7B%22value%22%3Atrue%7D%2C%22fsba%22%3A%7B%22value%22%3Afalse%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22nc%22%3A%7B%22value%22%3Afalse%7D%2C%22cmsn%22%3A%7B%22value%22%3Afalse%7D%2C%22auc%22%3A%7B%22value%22%3Afalse%7D%2C%22fore%22%3A%7B%22value%22%3Afalse%7D%2C%22sf%22%3A%7B%22value%22%3Afalse%7D%2C%22tow%22%3A%7B%22value%22%3Afalse%7D%7D%2C%22isListVisible%22%3Atrue%7D'
        yield scrapy.Request(fsbo_url, callback=self.start_main_requests
                             ,meta={"proxy":PROXY}
                             )

    def start_main_requests(self, response):
        yield scrapy.Request(self.start_url, callback=self.parse_property_list_html,
                             meta={"proxy":PROXY}
                             )
    
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

        yield scrapy.Request(
            url=api_url, 
            callback=self.parse_property_list_json, 
            method='PUT', 
            body=json.dumps(full_query),
            meta={"proxy":PROXY}
            )

    def parse_property_list_json(self, response):
        json_str = response.text
        json_dict = json.loads(json_str)
        search_results = json_dict['cat1']['searchResults']['mapResults']
        for apartment in search_results:
            lat = apartment['latLong'].get('latitude','')
            long = apartment['latLong'].get('longitude','')
            print(lat,long)
            yield {"Geo": (lat,long)}
    
