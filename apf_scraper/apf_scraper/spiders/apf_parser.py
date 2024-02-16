
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

    async def parse(self, response, **kwargs):
        page = response.meta.get('playwright_page')
        if not page:
            self.log(f"Received a non-Playwright response for URL: {response.url}", level=logging.WARNING)
            return
        
        try:
            # check if page is apartment complex or single unit 
            if await page.query_selector('#pricingView'):
                general_info = await self.parse_general_info(page,False)
                yield ApfGeneralInfoItem(**general_info)
                # Retrieve all units 
                unit_prices = await self.parse_unit_prices(page, general_info['PropertyId'])
                for unit in unit_prices:
                    yield ApfUnitItem(**unit)
            else:
                logging.info('single unit property encountered')
                general_info = await self.parse_general_info(page,True)
                yield ApfGeneralInfoItem(**general_info)
                # grab single unit price
                unit_price = await self.single_unit_price(page,general_info['PropertyId'])
                if unit_price:
                    yield ApfUnitItem(**unit_price)

        except Exception as e:
            self.log(f'An error occurred while parsing the page:{response.url} {str(e)}', level=logging.ERROR)

        finally:
            await page.close()

#  ======================= Retrieve General Info  =======================
    async def parse_general_info(self, page,is_single_unit):
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

        # parrallel requests for elements
        results = await asyncio.gather(*coroutines.values(), return_exceptions=True)
        results = {key: result if not isinstance(result, Exception) else None for key, result in zip(coroutines.keys(), results)}

        # retrieve all amenities 
        amenities = []
        if results['amenities_elements']:
            amenities = [amenity.strip() for amenity in await asyncio.gather(*(elem.text_content() for elem in results['amenities_elements'])) if amenity]

        # if single unit the name may be the address,
        if is_single_unit:
            property_name = results.get('property_name', '').strip()
            property_name_lower = property_name.lower()
            if 'unit' in property_name_lower:
                address = property_name_lower.split('unit')[0].strip()
            elif not results.get('address'):
                address = property_name
            else:
                address = results.get('address','').strip()
        else:
            address = results.get('address', '').strip()
        
        # handle empty values and return 
        general_info = {
            'PropertyName': results.get('property_name', '').strip(),
            'PropertyId': results.get('property_id', '').strip(),
            'PropertyUrl': page.url,
            'Address': address,
            'NeighborhoodLink': results.get('neighborhood_link', ''),
            'Neighborhood': results.get('neighborhood', '').strip(),
            'ReviewScore': float(results['reviews_element'].strip()) if results['reviews_element'] else 0,
            'VerifiedListing': 'verified' if results.get('verification') else 'Un-verified',
            'Amenities': amenities,
            'is_single_unit': 1 if is_single_unit else 0
        }
        return general_info
    
#  ======================= Retrieve Unit Pricing  =======================
    async def single_unit_price(self,page,property_id):
        detail_elements = await page.query_selector_all('.priceBedRangeInfoInnerContainer .rentInfoDetail')
        detail_texts = await asyncio.gather(*[element.text_content() for element in detail_elements])

        # check for studio 
        studio_flag = False
        if 'studio' in detail_texts[1].lower():
            studio_flag = True

        # make sure list is same length as details
        numbers = ['none' for _ in detail_texts]
        # retrieve number values from details using regular expression
        pattern = re.compile(r'\d+(?:[,.]\d+)*')
        for idx,text in enumerate(detail_texts):
            if text:
                extracted_numbers = pattern.findall(text.replace(',', ''))
                numbers[idx] = float(extracted_numbers[0]) if extracted_numbers else 'none'
                
        if studio_flag and len(numbers) > 1:
            numbers[1] = 0

        # avoid adding units without price
        if numbers[0] is None:
            raise ValueError("Missing details")
    
        return {'PropertyId':property_id,
            'MaxRent': numbers[0],
            'Model': 'single_unit',
            'Beds':numbers[1],
            'Baths':numbers[2],
            'SquareFootage':numbers[3]}
        

    async def handle_unit(self,unit,property_id):
            model, max_rent, beds, baths = await asyncio.gather(
                unit.get_attribute('data-model'),
                unit.get_attribute('data-maxrent'),
                unit.get_attribute('data-beds'),
                unit.get_attribute('data-baths')
            )

            # sq foot handled seperately on website 
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
        # process each unit place card returning only if it is unique
        for unit in units:
            unit_item = await self.handle_unit(unit, property_id)
            unique_id = tuple(unit_item.values())
            if unique_id not in unique_apartments:
                unique_apartments.add(unique_id)
                unit_items.append(unit_item)
        return unit_items
    

