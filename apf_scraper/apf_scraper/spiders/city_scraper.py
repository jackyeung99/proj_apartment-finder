import scrapy
import os 


class CityScraperSpider(scrapy.Spider):
    name = "city_scraper"

    def start_requests(self):
        self.links = self.get_links()
        # for city in self.links:
        yield scrapy.Request(
            url=self.links[0].strip(),
            callback=self.parse
        )

    def parse(self, response):
        sections = response.css('div#content > section')
    
        # population 
        pop_selector = sections.css('#city-population')

        # population by sex 
        pop_by_sex_selector = sections.css('#population-by-sex')

        # age 
        age_selector = sections.css('#median-income')

        # median rent
        rent_selector = sections.css('#median-rent')

        # cost of living 
        col_selector = sections.css('#cost-of-living-index')

        # poverty
        pov_selector = sections.css('#poverty-level')

        # crime
        crime_selector = sections.css('#crime')

        # pop densities
        pop_dens = sections.css('#population_density')

        # real estate taxes 
        real_estate_taxes = sections.css('#real-estate-taxes')

        # unemployment 
        unemployment = sections.css('#unemployment')

        # most common industries 
        industries = sections.css('#most-common-industries')

        # hospitals 
        hospitals = sections.css('#hospitals')

        # airports 
        airports = sections.css('#airports')

        # schools 
        schools = sections.css('#schools')



    def get_links(self):
        with open('city_stat_links.txt') as f:
            contents = f.readlines()
            return contents

        