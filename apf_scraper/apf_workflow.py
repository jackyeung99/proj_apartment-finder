

import time
from scrapy.crawler import CrawlerProcess
from scrapy.signalmanager import dispatcher
from scrapy import signals 
from apf_scraper.spiders.apf_crawler import ApfCrawlerSpider
from apf_scraper.spiders.apf_parser import ApfParserSpider
from apf_scraper.spiders.zillow_crawler import ZillowCrawlerSpider
from apf_scraper.spiders.zillow_parser import ZillowParserSpider

def run_spiders(city, state):
    start = time.time()
    links = []
    complexes = []

    # allow process of info between spiders
    def collect_links(item, response, spider):
        # Assume each item yielded by Spider1 has a 'url' key
        if spider.name == 'ApfCrawlerSpider':
            links.append(item['url'])
        elif spider.name == 'ZillowCrawlerSpider':
            complexes.append(item['Geo'])

    # Initialize crawler processes 
    process = CrawlerProcess()
    dispatcher.connect(collect_links, signal=signals.item_scraped)

    # run spiders
    process.crawl(ApfCrawlerSpider,city=city,state=state)
    process.crawl(ApfParserSpider,apartments_to_scrape = links)
    process.crawl(ZillowCrawlerSpider,city=city,state=state)
    process.crawl(ZillowParserSpider,apartments_to_scrape = complexes)


    end = time.time()
    print(f"runtime: {end-start}")
    
if __name__ == "__main__":
    with open('cities.txt','r') as f: 
        contents = f.readlines()
        
    for item in contents:
        split = item.split(',')
        run_spiders(split[0],split[1])

