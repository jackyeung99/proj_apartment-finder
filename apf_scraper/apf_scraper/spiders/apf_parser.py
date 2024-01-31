
import scrapy
from scrapy import Request
from playwright.async_api import async_playwright
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
        except FileNotFoundError:
            logging.critical(f'File not found: {links_file}')
            return []
        except json.JSONDecodeError:
            logging.error(f'Error decoding JSON from file: {links_file}')
            return []

    def start_requests(self):
        for url in self.links:
            yield Request(
                url=url,
                callback=self.parse,
                meta=dict(
			    playwright = True,
			    playwright_include_page = True, 
		    ))
        

    async def parse(self, response, **kwargs):
        logging.info(f"Request meta for URL {response.url}: {response.request.meta}")
        # Ensure 'playwright_page' is in response.meta before proceeding
        if 'playwright_page' in response.meta:
            page = response.meta['playwright_page']

            general_info = await self.parse_general_info(page)
            yield ApfGeneralInfoItem(**general_info)

            unit_prices = await self.parse_unit_prices(page, general_info['PropertyId'])
            for unit_price in unit_prices:
                yield unit_price

            await page.close()
        else:
            self.logger.warning(f"Received a non-Playwright response for URL: {response.url}")

    async def parse_general_info(self, page):
        property_name = await page.text_content('#propertyName')
        property_id = await page.evaluate('() => document.querySelector("body > div.mainWrapper > main").getAttribute("data-listingid")')
        property_url = page.url
        address = await page.text_content('#propertyAddressRow .delivery-address span')
        neighborhood_link = await page.get_attribute('#propertyAddressRow .neighborhoodAddress a', 'href')
        neighborhood = await page.text_content('#propertyAddressRow .neighborhoodAddress a')
        reviews_element = await page.query_selector('span.reviewRating')
        reviews = await reviews_element.text_content() if reviews_element else 'No reviews'
        verification = await page.text_content('#tooltipToggle span')
        amenities_elements = await page.query_selector_all('li.specInfo span')

        # Loop through the selected elements and get their text content
        amenities = []
        for element in amenities_elements:
            amenity_text = await element.text_content()
            amenities.append(amenity_text)

        return {
            'PropertyName': property_name.strip(),
            'PropertyId': property_id.strip(),
            'PropertyUrl': property_url.strip(),
            'Address': address.strip() if address.strip() else '',
            'NeighborhoodLink': neighborhood_link.strip(),
            'Neighborhood': neighborhood.strip(),
            'ReviewScore': reviews.strip(),
            'VerifiedListing': verification.strip(),
            'Amenities': amenities
        }

    async def parse_unit_prices(self, page, property_id):
        units = await page.query_selector_all('.unitContainer')
        unique_apartments = set()
        unit_items = []

        for unit in units:
            model = await unit.get_attribute('data-model')
            max_rent = await unit.get_attribute('data-maxrent')
            beds = await unit.get_attribute('data-beds')
            baths = await unit.get_attribute('data-baths')
            square_footage = await unit.get_attribute('.sqftColumn span:nth-of-type(2)')
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
                unit_items.append(item)

        return unit_items
