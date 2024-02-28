
import re
import scrapy
from scrapy import Request

class ApfCrawlerSpider(scrapy.Spider):
    name = "apf_crawler"
    allowed_domains = ["www.apartments.com"]

    def __init__(self, city='austin', state='tx', housing_type="apartments", *args, **kwargs):
        super(ApfCrawlerSpider, self).__init__(*args, **kwargs)
        self.city = city.lower()
        self.state = state.lower()
        self.housing_type = housing_type.lower()

    def start_requests(self):
        '''Start workflow for link crawler'''
        initial_url = f"https://www.apartments.com/{self.housing_type}/{self.city}-{self.state}/"
        yield Request(url=initial_url, callback=self.parse_initial,meta=dict(
			    playwright = True,
			    playwright_include_page = True,))

    def parse_initial(self, response):
        ''' Pagination logic to scrape through all available pages'''
        max_page_num = self.extract_max_page(response)
        if max_page_num:
            for page_num in range(1,max_page_num + 1):
                url = f"https://www.apartments.com/{self.housing_type}/{self.city}-{self.state}/{page_num}/"
                yield Request(url=url, callback=self.parse,meta=dict(
			    playwright = True,
			    playwright_include_page = True,))

    def extract_max_page(self, response):
        ''' Retrieve max page to limit pagination'''
        page_range_text = response.css(".pageRange::text").get()
        if page_range_text:
            return int(re.search(r'Page \d+ of (\d+)', page_range_text).group(1))
        return 0

    def parse(self, response):
        ''' Retrieve all unique apartment links'''
        link_selector = 'article.placard a.property-link::attr(href)'
        links = set(response.css(link_selector).getall())
        for link in links:
            yield {'url': link}

    def closed(self, reason):
        print(f"Spider closed because {reason}")
