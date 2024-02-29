import scrapy
import json
from urllib.parse import urlencode
from pprint import pprint
from apf_scraper.items import ApartmentUnit, ApartmentComplex, leasing_info, ComplexAmmenities, UnitAmmenities


class ZillowParserSpider(scrapy.Spider):
    name = "zillow_parser"
    allowed_domains = ["www.zillow.com"]


    def __init__(self, apartments_to_scrape, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.parse_list = [(40.808674, -73.93156, ''), (40.588963, -73.79774, 2355011519), (40.706898, -73.80466, 2176833280), (40.709915, -73.79607, 1003190227), (40.755264, -73.82179, '')]
        self.parse_list = apartments_to_scrape
        
    def start_requests(self):
        fsbo_url = r'https://www.zillow.com/apartments/bronx-ny/estela-properties/CJbB6G/'
        yield scrapy.Request(fsbo_url, callback=self.start_requests)

    def start_requests(self):
        for items in self.parse_list:
            url = "https://www.zillow.com/graphql/"

            payload = json.dumps({
            "operationName": "BuildingQuery",
            "variables": {
                "cache": False,
                "latitude": items[0],
                "longitude": items[1],
                "lotId": None,
                "update": False
            },
            "extensions": {
                "persistedQuery": {
                "version": 1,
                "sha256Hash": "09d671af3d7c05bb225dac62666d0e9e1d5d629bc82e8e124827804903d2fcd0"
                }
            }
            })
            headers = {
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Cookie': 'zguid=24|%2423c166ac-11ce-4c3b-b80b-2c0f026f1321; _ga=GA1.2.2035172985.1706029735; _gac_UA-21174015-56=1.1706029735.CjwKCAiA5L2tBhBTEiwAdSxJX3r4O2-aA744uBsdFfhwX0J3gvsl74g5JJS7YYDXGhKXOeML0CkvfRoCh5kQAvD_BwE; zjs_anonymous_id=%2223c166ac-11ce-4c3b-b80b-2c0f026f1321%22; zjs_user_id=null; zg_anonymous_id=%22a8e65ed2-13b4-4083-a48b-fedc124721b1%22; _gcl_aw=GCL.1706029735.CjwKCAiA5L2tBhBTEiwAdSxJX3r4O2-aA744uBsdFfhwX0J3gvsl74g5JJS7YYDXGhKXOeML0CkvfRoCh5kQAvD_BwE; _gcl_au=1.1.1146248459.1706029735; _pxvid=16df7c3f-ba12-11ee-ae52-e44a4ae8a06d; __pdst=d2cf178b56ea4c5ca6de8451cd26d08d; _hp2_id.1215457233=%7B%22userId%22%3A%225049024401355714%22%2C%22pageviewId%22%3A%226161518787143574%22%2C%22sessionId%22%3A%225620592693318848%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%224.0%22%7D; _pin_unauth=dWlkPVpqY3laamRsT1RNdE16STJNUzAwWVdZM0xXRXhNV0l0TWpRME1qUmlNbUk0TURZNA; _clck=1j31lwi%7C2%7Cfin%7C0%7C1483; _uetvid=17f749d0ba1211eeb8e71bb346e80808; zgsession=1|e7944311-f61d-45c5-b2bc-549c6d187758; optimizelyEndUserId=oeu1708959617349r0.7240828754154476; pjs-last-visited-page=/research/data/; pjs-pages-visited=1; zgcus_aeut=AEUUT_c04efe40-d4b7-11ee-a590-5659d18b21ed; zgcus_aeuut=AEUUT_c04efe40-d4b7-11ee-a590-5659d18b21ed; JSESSIONID=36F73D2E40E96B15BB838D191C6C263D; search=6|1711591741595%7Crect%3D41.007916244996316%2C-73.52512167382812%2C40.38633696547364%2C-74.43424032617187%26rid%3D6181%26disp%3Dmap%26mdm%3Dauto%26p%3D1%26z%3D0%26listPriceActive%3D1%26type%3Dcondo%2Capartment_duplex%2Cmobile%2Cland%26fs%3D0%26fr%3D1%26mmm%3D0%26rs%3D0%26ah%3D0%26singlestory%3D0%26housing-connector%3D0%26abo%3D0%26garage%3D0%26pool%3D0%26ac%3D0%26waterfront%3D0%26finished%3D0%26unfinished%3D0%26cityview%3D0%26mountainview%3D0%26parkview%3D0%26waterview%3D0%26hoadata%3D1%26zillow-owned%3D0%263dhome%3D0%26featuredMultiFamilyBuilding%3D0%26student-housing%3D0%26income-restricted-housing%3D0%26military-housing%3D0%26disabled-housing%3D0%26senior-housing%3D0%26excludeNullAvailabilityDates%3D0%26isRoomForRent%3D0%26isEntirePlaceForRent%3D1%26commuteMode%3Ddriving%26commuteTimeOfDay%3Dnow%09%096181%09%7B%22isList%22%3Atrue%2C%22isMap%22%3Atrue%7D%09%09%09%09%09; AWSALB=kssNkudmWFzYjnoUDDSy2db7qHDx74KvvOVoZfP7kpsqkk2e3ZFNEDvh+77rGCy/XlJVN3XyelB5uRl3SvAQNR6auOi8nB8AoZSRWeF5JkJtCmcgodZ4wnfPHKIs; AWSALBCORS=kssNkudmWFzYjnoUDDSy2db7qHDx74KvvOVoZfP7kpsqkk2e3ZFNEDvh+77rGCy/XlJVN3XyelB5uRl3SvAQNR6auOi8nB8AoZSRWeF5JkJtCmcgodZ4wnfPHKIs',
            'Origin': 'https://www.zillow.com',
            'Pragma': 'no-cache',
            'Referer': 'https://www.zillow.com/b/building/40.808674,-73.93156_ll/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'accept': '*/*',
            'client-id': 'vertical-living',
            'content-type': 'application/json',
            'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
            }
        
            yield scrapy.Request(
                url=url,
                method='POST',
                headers=headers,
                body=payload,
                callback=self.parse_property_page_json
            )
            
                        

    def parse_property_page_json(self, response):
        json_dict = json.loads(response.text)
        data_dict = json_dict.get('data', {})
        pprint(data_dict['building'].keys())
        

