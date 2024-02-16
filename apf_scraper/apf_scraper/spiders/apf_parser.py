
import scrapy
from scrapy import Request
from playwright.async_api import async_playwright
import asyncio
import logging
import os
import re
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

    def start_requests(self):
        for url in self.links:
            yield Request(
                url=url,
                callback=self.parse,
                meta={
                'playwright': True,
                'playwright_include_page': True,
                })
        
#  ======================= Scraping workflow/logic =======================

    async def parse(self, response, **kwargs):
        page = response.meta.get('playwright_page')
        if not page:
            self.log(f"Received a non-Playwright response for URL: {response.url}", level=logging.WARNING)
            return
        
        try:
            general_info = await self.parse_general_info(page)
            yield ApfGeneralInfoItem(**general_info)
            print(general_info['PropertyName'])
            if await page.query_selector('#pricingView'):
                unit_prices = await self.parse_unit_prices(page, general_info['PropertyId'])
                print(unit_prices)
                for unit in unit_prices:
                    yield ApfUnitItem(**unit)
            else:
                print('single unit encountered')
                unit_price = await self.single_unit_price(page,general_info['PropertyId'])
                yield ApfUnitItem(**unit_price)

        except Exception as e:
            self.log(f'An error occurred while parsing the page:{response.url} {str(e)}', level=logging.ERROR)

        finally:
            await page.close()

#  ======================= Retrieve General Info  =======================
    async def parse_general_info(self, page):
        coroutines = {
        'property_name': page.text_content('#propertyName'),
        'address': page.text_content('#propertyAddressRow .delivery-address span'),
        'property_id': page.evaluate('''() => document.querySelector("body > div.mainWrapper > main").getAttribute("data-listingid")'''),
        'neighborhood_link': page.get_attribute('#propertyAddressRow .neighborhoodAddress a', 'href'),
        'neighborhood': page.text_content('#propertyAddressRow .neighborhoodAddress a'),
        'reviews_element': page.text_content('span.reviewRating'),
        'verification': page.text_content('#tooltipToggle span'),
        'amenities_elements': page.query_selector_all('li.specInfo span')
         }

        results = await asyncio.gather(*coroutines.values(), return_exceptions=True)
        results = {key: result if not isinstance(result, Exception) else None for key, result in zip(coroutines.keys(), results)}

        amenities = []
        if results['amenities_elements']:
            amenities = [amenity.strip() for amenity in await asyncio.gather(*(elem.text_content() for elem in results['amenities_elements'])) if amenity]

        general_info = {
            'PropertyName': results['property_name'].strip() if results['property_name'] else '',
            'PropertyId': results['property_id'] if results['property_id'] else '',
            'PropertyUrl': page.url,
            'Address': results['address'].strip() if results['address'] else '',
            'NeighborhoodLink': results['neighborhood_link'].strip() if results['neighborhood_link'] else '',
            'Neighborhood': results['neighborhood'].strip() if results['neighborhood'] else '',
            'ReviewScore': float(results['reviews_element'].strip()) if results['reviews_element'] else 0,
            'VerifiedListing':  'verified' if results['verification'] else 'Un-verified',
            'Amenities': amenities
            }
        
        return general_info
    
#  ======================= Retrieve Unit Pricing  =======================
    async def single_unit_price(self,page,property_id):
        detail_elements = await page.query_selector_all('.priceBedRangeInfoInnerContainer .rentInfoDetail')
        detail_texts = await asyncio.gather(*[element.text_content() for element in detail_elements])

        pattern = re.compile(r'\d+(?:[,.]\d+)*')
        numbers = []
        for text in detail_texts:
            if text:
                extracted_numbers = pattern.findall(text.replace(',', ''))
                numbers.extend(extracted_numbers)

        try:
            max_rent = float(numbers[0]) if len(numbers) > 0 else None
            beds = float(numbers[1]) if len(numbers) > 1 else None
            baths = float(numbers[2]) if len(numbers) > 2 else None
            square_footage = float(numbers[3]) if len(numbers) > 3 else None

            # set threshold for which values can be none
            if None in [max_rent, beds, baths, square_footage]:
                raise ValueError("Missing details")

            # fix me: return dictionary not unit item
            return ApfUnitItem(
                PropertyId=property_id,
                MaxRent=max_rent,
                Model='single_unit',
                Beds=beds,
                Baths=baths,
                SquareFootage=square_footage
            )
        except (ValueError, IndexError) as e:
            logging.error(f"Error processing details for property {property_id}: {e}")
            return None

    async def handle_unit(self,unit,property_id):
            model, max_rent, beds, baths = await asyncio.gather(
                unit.get_attribute('data-model'),
                unit.get_attribute('data-maxrent'),
                unit.get_attribute('data-beds'),
                unit.get_attribute('data-baths')
            )

            square_footage_element = await unit.query_selector('.sqftColumn span:nth-of-type(2)')
            square_footage = await square_footage_element.text_content() if square_footage_element else ''

            return {'PropertyId':property_id,
                'MaxRent': max_rent,
                'Model': model,
                'Beds':beds,
                'Baths':baths,
                'SquareFootage':square_footage}
            
    async def parse_unit_prices(self, page, property_id):
        units = await page.query_selector_all('.unitContainer')
        unit_items = []
        unique_apartments = set()
        for unit in units:
            unit_item = await self.handle_unit(unit, property_id)
            unique_id = tuple(unit_item.values())
            if unique_id not in unique_apartments:
                unique_apartments.add(unique_id)
                unit_items.append(unit_item)
        return unit_items
    

