
import scrapy
from scrapy import Request
import chompjs
import logging
import json
import re
from apf_scraper.items import ApartmentUnit, ApartmentComplex, leasing_info, ComplexAmmenities, UnitAmmenities

class ApfParserSpider(scrapy.Spider):
    name = "apf_parser"
    custom_settings = {
        'ITEM_PIPELINES': {
            'apf_scraper.pipelines.ApartmentGeneralInfoPipeline': 100,
            'apf_scraper.pipelines.UnitPricesPipeline': 200,
        },
    }

    def __init__(self, apartments_to_scrape, *args, **kwargs):
        super(ApfParserSpider, self).__init__(*args, **kwargs)
        self.parse_list = apartments_to_scrape

    def start_requests(self):
        for idx,url in enumerate(self.links[:1]):
            print(f'page:{idx} out of {len(self.links)}')
            yield Request(
                url=url,
                callback=self.parse,
                meta={
                'playwright': True,
                'playwright_include_page': True,
                })
        
#  ======================= Scraping workflow/logic =======================

    def parse(self, response, **kwargs):
        page = response.meta.get('playwright_page')
        if not page:
            self.log(f"Received a non-Playwright response for URL: {response.url}", level=logging.WARNING)
            return
        
        try:
            apartment_json = self.extract_json(response)
            print(apartment_json.keys())
            # for unit in apartment_json['rentals']:
            #     print(unit.keys())

        except Exception as e:
            self.log(f'An error occurred while parsing the page:{response.url} {str(e)}', level=logging.ERROR)

        finally:
            page.close()

    def extract_json(self,response):
        script_text = response.xpath("//script[contains(., 'startup.init')]/text()").get()
        if script_text:
            json_str_match = re.search(r'startup\.init\(\s*(\{.*?\})\s*\);', script_text, re.DOTALL)
            if json_str_match:
                json_like_str = json_str_match.group(1)
                converted = chompjs.parse_js_object(json_like_str)

        return converted
    
    # async def retrieve_info(self,apartment_json):
    #     return {
    #         'PropertyName': apartment_json['ListingName'],
    #         'PropertyId': apartment_json['listingId'],
    #         'PropertyUrl': response.url,
    #         'Address': apartment_json['ListingAddress'],
    #         'Neighborhood':,
    #         'ReviewScore': float(results['reviews_element'].strip()) if results['reviews_element'] else 0,
    #         'VerifiedListing': 'verified' if results.get('verification') else 'Un-verified',
    #         'Amenities': amenities
    #     }
        

    # async def retrieve_unit(self,unit_json):
    #     return {'PropertyId':unit_json['RentalKey'],
    #             'MaxRent': unit_json['MaxRent'],
    #             'Model': unit_json['Mode'],
    #             'Beds':unit_json['Beds'],
    #             'Baths':unit_json['Baths'],
    #             'SquareFootage': unit_json['SquareFeet']}


