import scrapy 
import re
import json
from datetime import date

import sys
import os 

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
print(repo_root)
sys.path.append(repo_root)



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

        # city name/state 
        location = response.css('div#content > h1 > span::text').extract_first().split(',')
        city_data['CityName'] = location[0].strip()
        city_data['State'] = location[1].strip()
    
        # population 
        pop_section = sections.css('#city-population')
        population_number = pop_section.xpath('b[contains(text(), "Population in")]/following-sibling::text()[1]').extract_first(default='').strip()
        population_change_number = pop_section.xpath('b[contains(text(), "Population change since 2000")]/following-sibling::text()[1]').extract_first(default='').strip().replace('%','')
        
        city_data['Population'] = int(population_number.replace(',','').split(' ')[0]) 
        city_data['Population_change'] = float(population_change_number.replace('+',''))

        # population by sex 
        pop_by_sex_selector = sections.css('#population-by-sex')
        pop_numbers = pop_by_sex_selector.xpath('div/table/tr/td[2]/text()').extract()

        city_data['Population_males'] = float(self.extract_numbers(pop_numbers[0]))
        city_data['Population_females'] = float(self.extract_numbers(pop_numbers[1]))

        # age 
        age_selector = sections.css('#median-age')
        ages = age_selector.xpath('div/table/tr/td[2]/text()').extract()
        city_data['Median_resident_age'] = float(ages[0].replace('years','').strip())
    
        # median income 
        income_selector = sections.css('#median-income')
        table_info = income_selector.xpath('div/table/tr/td[2]/text()').extract()
        median_household_income_2000 = income_selector.xpath('b[contains(text(), "Estimated median household income in")]/following-sibling::b[contains(text(), "it was")]/following-sibling::text()[1]').extract_first(default='').strip()
        per_capita_income_2000 = income_selector.xpath('b[contains(text(), "Estimated per capita income in")]/following-sibling::b[contains(text(), "it was")]/following-sibling::text()[1]').extract_first(default='').strip()
        per_capita_income_2022 = income_selector .xpath('b[contains(text(), "Estimated per capita income in")]/following-sibling::text()[1]').extract_first(default='').strip()

        city_data['Income_2022'] = int(self.extract_numbers(table_info[0]))
        city_data['Income_2000'] = int(self.extract_numbers(median_household_income_2000))
        city_data['Per_capita_income_2022'] = int(self.extract_numbers(per_capita_income_2022))
        city_data['Per_capita_income_2000'] = int(self.extract_numbers(per_capita_income_2000))
  
        # Houses 
        median_house_value_2022 = income_selector.xpath('b[contains(text(), "Estimated median house or condo value in")]/following-sibling::b[contains(text(), "it was")]/following-sibling::text()[1]').extract_first(default='').strip()
        city_data['Median_house_value_2000'] = int(self.extract_numbers(table_info[1]))
        city_data['Median_house_value_2022'] = int(self.extract_numbers(median_house_value_2022))

        # Apartment rent 
        rent_selector = sections.css('#median-rent')
        median_gross_rent_value = rent_selector.xpath('p/b[contains(text(),"Median gross rent in")]/following-sibling::text()[1]').extract_first(default='').strip()
        city_data['Median_gross_rent_2022'] = int(self.extract_numbers(median_gross_rent_value).replace('.',''))
      
        # cost of living 
        col_selector = sections.css('#cost-of-living-index')
        cost_of_living_index = col_selector.xpath('b[contains(text(), "cost of living index in")]/following-sibling::text()[1]').extract_first(default='').strip()
        city_data['Cost_of_living'] = float(cost_of_living_index)

        # poverty
        pov_selector = sections.css('#poverty-level')
        poverty_percentage = pov_selector.xpath('b[contains(text(), "Percentage of residents living in poverty in")]/following-sibling::text()[1]').extract_first(default='').strip()
        city_data['Poverty_percentage'] = float(self.extract_numbers(poverty_percentage))

        # crime
        crime_selector = sections.css('#crime')
        crime_data = []
    
        years = crime_selector.css('table > thead > tr> th > h4::text').extract()[1:]
        for year in years: 
            crime_data.append({'Year': year})

        for row in crime_selector.css('table > tbody > tr'):
            crime_type = row.css('td')[0].css('b::text').get().replace(' ','_')
            for idx,col in enumerate(row.css('td')[1:]):
                crime_data[idx][crime_type] = eval(self.extract_numbers(col.css('small::text').get()))

        city_data['crime'] = crime_data

        # land area 
        land_area_selector = response.css('section#population-density p')
        land_area = land_area_selector.xpath('b[contains(text(), "Land area:")]/following-sibling::text()[1]').extract_first(default='').strip()
        city_data['Land_area'] = float(self.extract_numbers(land_area)) 

        # Population density
        population_density = land_area_selector.xpath('b[contains(text(), "Population density:")]/following-sibling::text()[1]').extract_first(default='').strip()
        city_data['Population_density'] = int(self.extract_numbers(population_density))

        # real estate taxes 
        taxes_selector = sections.css('#real-estate-taxes')
        taxes_with_mortgage = taxes_selector.xpath('p/b[contains(text(), "Median real estate property taxes paid for housing units with mortgages in")]/following-sibling::text()[1]').re(r'\(([^)]+)\)')
        taxes_no_mortgage = taxes_selector.xpath('p/b[contains(text(), "Median real estate property taxes paid for housing units with no mortgage in")]/following-sibling::text()[1]').re(r'\(([^)]+)\)')

        if taxes_with_mortgage:
            city_data['Tax_with_mortgage'] = float(self.extract_numbers(taxes_with_mortgage[0]))

        if taxes_no_mortgage:
            city_data['Tax_no_mortgage'] = float(self.extract_numbers(taxes_no_mortgage[0]))

        # unemployment 
        unemployment_selector = sections.css('#unemployment')
        city_data['Unemployment'] = float(self.extract_numbers(unemployment_selector.xpath('div/table/tr[1]/td[2]/text()').extract_first()))

        # most common industries 
        # industries = sections.css('#most-common-industries')

        # # hospitals 
        # hospitals = sections.css('#hospitals')

        # # airports 
        # airports = sections.css('#airports')

        # # schools 
        # schools = sections.css('#schools')

        print(city_data)
        self.main_data.append(city_data)


    def get_links(self):
        links = os.path.join(repo_root, 'src', 'scraper', 'city_stat_links.txt')
        with open(links) as f:
            contents = f.readlines()
            return contents

    def closed(self, reason):
        date_today = date.today()
        data_path = os.path.join(repo_root, f"data/raw_data/{date_today}_city_data.jsonl")
        with open(data_path, 'w') as f:
            for city in self.main_data:
                json_line = json.dumps(city) + "\n" 
                f.write(json_line)