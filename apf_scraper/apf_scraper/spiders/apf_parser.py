
import scrapy
from scrapy import Request
import chompjs
import logging
import json
import re
from items import Apartment


class ApfParserSpider(scrapy.Spider):
    name = "apf_parser"

    def __init__(self, apartments_to_scrape, file, *args, **kwargs):
        super(ApfParserSpider, self).__init__(*args, **kwargs)
        self.file = file
        self.parse_list = apartments_to_scrape

    def start_requests(self):
        for idx,url in enumerate(self.links):
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
            # yield json for each apartment
            yield Apartment({'apartment_json': self.extract_json(response)})
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

