
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
        page = response.meta.get('playwright_page')
        if not page:
            self.log(f"Received a non-Playwright response for URL: {response.url}", level=logging.WARNING)
            return
        
        try:
            general_info = await self.parse_general_info(page)
            # Check if the property name indicates a single unit
            if 'unit' in general_info['PropertyName'].lower():
                # Log that a single unit page was found and then skip it
                self.log(f"Single unit page detected, skipping URL: {response.url}", level=logging.INFO)
                return  # This will exit the parse method and skip further processing
            
            yield ApfGeneralInfoItem(**general_info)
            
            # If it's not a single unit, continue processing unit prices
            unit_prices = await self.parse_unit_prices(page, general_info['PropertyId'])
            for unit_price in unit_prices:
                yield unit_price

        except Exception as e:
            self.log(f'An error occurred while parsing the page:{response.url} {str(e)}', level=logging.ERROR)

        finally:
            await page.close()


    async def parse_general_info(self, page):
        property_name = (await page.text_content('#propertyName')).strip()
        # Initialize address variable outside the conditional scope for broader accessibility
        address = ''
        if 'unit' in property_name.strip().lower():
            # If 'unit' is in property_name, set address as everything before 'unit'
            address = property_name.split('unit', 1)[0].strip()  # Splits at the first occurrence of 'unit' and takes the first part
        else:
            # If 'unit' is not in property_name, fetch address from the designated element
            address = await page.text_content('#propertyAddressRow .delivery-address span')

        property_id = await page.evaluate('''() => document.querySelector("body > div.mainWrapper > main").getAttribute("data-listingid")''')
        property_url = page.url
        neighborhood_link = (await page.get_attribute('#propertyAddressRow .neighborhoodAddress a', 'href')).strip()
        neighborhood = (await page.text_content('#propertyAddressRow .neighborhoodAddress a')).strip()
        reviews_element = await page.query_selector('span.reviewRating')
        reviews = (await reviews_element.text_content()).strip() if reviews_element else 'No reviews'
        verification = (await page.text_content('#tooltipToggle span')).strip()

        # Loop through the selected elements and get their text content for amenities
        amenities_elements = await page.query_selector_all('li.specInfo span')
        amenities = [(await element.text_content()).strip() for element in amenities_elements]

        return {
            'PropertyName': property_name,
            'PropertyId': property_id,
            'PropertyUrl': property_url,
            'Address': address,
            'NeighborhoodLink': neighborhood_link,
            'Neighborhood': neighborhood,
            'ReviewScore': reviews,
            'VerifiedListing': verification,
            'Amenities': amenities
        }

    # async def single_unit_price(self,page,property_id):
    #     details = ApfUnitItem(
    #         PropertyId=property_id,
    #         MaxRent=None,
    #         Model= 'single_unit',
    #         Beds=None,
    #         Baths=None,
    #         SquareFootage=None
    #     )

    #     # Use Playwright's query_selector method to grab each piece of information
    #     rent_element = await page.query_selector('p.rentInfoDetail')
    #     if rent_element:
    #         details['MaxRent'] = await rent_element.text_content()

    #     bedrooms_element = await page.query_selector('div.priceBedRangeInfoInnerContainer:has(p.rentInfoLabel:has-text("Bedrooms")) p.rentInfoDetail')
    #     if bedrooms_element:
    #         details['Beds'] = await bedrooms_element.text_content()

    #     bathrooms_element = await page.query_selector('div.priceBedRangeInfoInnerContainer:has(p.rentInfoLabel:has-text("Bathrooms")) p.rentInfoDetail')
    #     if bathrooms_element:
    #         details['Baths'] = await bathrooms_element.text_content()

    #     square_feet_element = await page.query_selector('div.priceBedRangeInfoInnerContainer:has(p.rentInfoLabel:has-text("Square Feet")) p.rentInfoDetail')
    #     if square_feet_element:
    #         details['SquareFootage'] = await square_feet_element.text_content()

    #     # Clean up the extracted text, if necessary
    #     for key in details:
    #         if details[key]:
    #             details[key] = details[key].strip()

    #     return details


    async def parse_unit_prices(self, page, property_id):
        units = await page.query_selector_all('.unitContainer')
        unique_apartments = set()
        unit_items = []

        for unit in units:
            model = await unit.get_attribute('data-model')
            max_rent = await unit.get_attribute('data-maxrent')
            beds = await unit.get_attribute('data-beds')
            baths = await unit.get_attribute('data-baths')

            square_footage_element = await unit.query_selector('.sqftColumn span:nth-of-type(2)')
            square_footage = await square_footage_element.text_content() if square_footage_element else ''
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

