import scrapy
import os 
import re
import json
from datetime import date


class CityScraperSpider(scrapy.Spider):
    name = "city_scraper"

    def __init__(self, name: str | None = None):
        super().__init__(name)
        self.main_data = []

    @staticmethod
    def extract_numbers(string):
        return re.sub(r'[^\d.]', '', string).strip()

    def start_requests(self):
        self.links = self.get_links()
        for city in self.links:
            yield scrapy.Request(
                url=city.strip(),
                callback=self.parse
            )

        
    def parse(self, response):
        city_data = {}
        sections = response.css('div#content > section')
    
        # population 
        pop_section = sections.css('#city-population')
        population_number = pop_section.xpath('b[contains(text(), "Population in 2021")]/following-sibling::text()[1]').extract_first(default='').strip()
        population_change_number = pop_section.xpath('b[contains(text(), "Population change since 2000")]/following-sibling::text()[1]').extract_first(default='').strip().replace('%','')
        
        city_data['population'] = population_number.replace(',','').split(' ')[0]
        city_data['population_change'] = population_change_number.replace('+','')

        # population by sex 
        pop_by_sex_selector = sections.css('#population-by-sex')
        pop_numbers = pop_by_sex_selector.xpath('div/table/tr/td[1]/text()').extract()

        city_data['males'] = self.extract_numbers(pop_numbers[0])
        city_data['females'] = self.extract_numbers(pop_numbers[1])

        # age 
        age_selector = sections.css('#median-age')
        ages = age_selector.xpath('div/table/tr/td[2]/text()').extract()
        city_data['median_resident_age'] = ages[0].replace('years','').strip()
    
        # median income 
        income_selector = sections.css('#median-income')
        table_info = income_selector.xpath('div/table/tr/td[2]/text()').extract()
        median_household_income_2000 = income_selector.xpath('b[contains(text(), "Estimated median household income in 2021:")]/following-sibling::b[contains(text(), "it was")]/following-sibling::text()[1]').extract_first(default='').strip()
        per_capita_income_2000 = income_selector.xpath('b[contains(text(), "Estimated per capita income in 2021:")]/following-sibling::b[contains(text(), "it was")]/following-sibling::text()[1]').extract_first(default='').strip()
        per_capita_income_2021 = income_selector .xpath('b[contains(text(), "Estimated per capita income in 2021:")]/following-sibling::text()[1]').extract_first(default='').strip()

        city_data['median_household_income_2021'] = self.extract_numbers(table_info[0])
        city_data['median_household_income_2000'] = self.extract_numbers(median_household_income_2000)
        city_data['per_capita_income_2021'] = self.extract_numbers(per_capita_income_2021)
        city_data['per_capita_income_2000'] = self.extract_numbers(per_capita_income_2000)
  
        # Houses 
        median_house_value_2000 = income_selector.xpath('b[contains(text(), "Estimated median house or condo value in 2021:")]/following-sibling::b[contains(text(), "it was")]/following-sibling::text()[1]').extract_first(default='').strip()
        city_data['median_house_value_2021'] = self.extract_numbers(table_info[1])
        city_data['median_house_value_2000'] = self.extract_numbers(median_house_value_2000)

        # Apartment rent 
        rent_selector = sections.css('#median-rent')
        median_gross_rent_value = rent_selector.xpath('p/b[contains(text(),"Median gross rent in 2021:")]/following-sibling::text()[1]').extract_first(default='').strip()
        city_data['median_gross_rent_2021'] = self.extract_numbers(median_gross_rent_value)
      
        # cost of living 
        col_selector = sections.css('#cost-of-living-index')
        cost_of_living_index = col_selector.xpath('b[contains(text(), "cost of living index in")]/following-sibling::text()[1]').extract_first(default='').strip()
        city_data['cost_of_living_index'] = cost_of_living_index

        # poverty
        pov_selector = sections.css('#poverty-level')
        poverty_percentage = pov_selector.xpath('b[contains(text(), "Percentage of residents living in poverty in")]/following-sibling::text()[1]').extract_first(default='').strip()
        city_data['poverty_percentage'] = self.extract_numbers(poverty_percentage)

        # crime
        crime_selector = sections.css('#crime')
        crime_data = []
    
        years = crime_selector.css('table > thead > tr> th > h4::text').extract()[1:]
        for year in years: 
            crime_data.append({'year': year})

        for row in crime_selector.css('table > tbody > tr'):
            crime_type = row.css('td')[0].css('b::text').get()
            for idx,col in enumerate(row.css('td')[1:]):
                crime_data[idx][crime_type] = self.extract_numbers(col.css('small::text').get())

        city_data['crime'] = crime_data

        # land area 
        land_area_selector = response.css('section#population-density p')
        land_area = land_area_selector.xpath('b[contains(text(), "Land area:")]/following-sibling::text()[1]').extract_first(default='').strip()
        city_data['land_area'] = land_area

        # Population density
        population_density = land_area_selector.xpath('b[contains(text(), "Population density:")]/following-sibling::text()[1]').extract_first(default='').strip()
        city_data['population_density(per square mile)'] = population_density

        # real estate taxes 
        taxes_selector = sections.css('#real-estate-taxes')
        taxes_with_mortgage = taxes_selector.xpath('p/b[contains(text(), "Median real estate property taxes paid for housing units with mortgages in 2021:")]/following-sibling::text()[1]').re(r'\(([^)]+)\)')
        taxes_no_mortgage = taxes_selector.xpath('p/b[contains(text(), "Median real estate property taxes paid for housing units with no mortgage in 2021:")]/following-sibling::text()[1]').re(r'\(([^)]+)\)')

        if taxes_with_mortgage:
            city_data['tax_percentage_with_mortgage'] = self.extract_numbers(taxes_with_mortgage[0])

        if taxes_no_mortgage:
            city_data['tax_percentage_no_mortgage'] = self.extract_numbers(taxes_no_mortgage[0])

        # unemployment 
        unemployment_selector = sections.css('#unemployment')
        city_data['unemployment_rate'] = self.extract_numbers(unemployment_selector.xpath('div/table/tr[1]/td[2]/text()').extract_first())

        # most common industries 
        # industries = sections.css('#most-common-industries')

        # # hospitals 
        # hospitals = sections.css('#hospitals')

        # # airports 
        # airports = sections.css('#airports')

        # # schools 
        # schools = sections.css('#schools')


        self.main_data.append(city_data)


    def get_links(self):
        with open('city_stat_links.txt') as f:
            contents = f.readlines()
            return contents

    def closed(self, reason):
        date_today = date.today()
        data_path = os.path.join('..', f"data/raw_data/{date_today}_cityinfo.json")
        with open(data_path, 'w') as f:
            json.dump(self.main_data, f, indent=4)