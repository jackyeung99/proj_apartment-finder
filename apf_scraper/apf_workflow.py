
import asyncio
from twisted.internet import asyncioreactor
asyncioreactor.install(asyncio.get_event_loop())

import time
from datetime import date
import os
from scrapy.crawler import CrawlerRunner
from scrapy.signalmanager import dispatcher
from scrapy import signals 
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings

# import spiders
from apf_scraper.spiders.apf_crawler import ApfCrawlerSpider
from apf_scraper.spiders.apf_parser import ApfParserSpider
from apf_scraper.spiders.zillow_crawler import ZillowCrawlerSpider
from apf_scraper.spiders.zillow_parser import ZillowParserSpider

''' Run spiders sequentially, while feeding in the data of the crawler spiders into the parsers'''
@defer.inlineCallbacks
def run_spiders_for_city(city, state, file):
    links = []
    complexes = []
    
    settings = get_project_settings()
    configure_logging(settings)
    runner = CrawlerRunner(settings)

    def collect_links(item, response, spider):
        if spider.name == 'apf_crawler':
            links.append(item['url'])
        elif spider.name == 'zillow_crawler':
            complexes.append(item['Geo'])

    dispatcher.connect(collect_links, signal=signals.item_scraped)

    yield runner.crawl(ApfCrawlerSpider, city=city, state=state)
    yield runner.crawl(ApfParserSpider, apartments_to_scrape=links, file=file)
    yield runner.crawl(ZillowCrawlerSpider, city=city, state=state)
    yield runner.crawl(ZillowParserSpider, apartments_to_scrape=complexes, file=file)

 
@defer.inlineCallbacks
def run_for_all_cities(cities):
    start = time.time()
    for location in cities[5:]:
        city, state = location.split(',')
        file = get_file(city.strip(),state.strip())
        yield run_spiders_for_city(city.strip(), state.strip(),file)
    print(f"all cities scraped, total time{time.time()-start}")


def get_file(city,state):
    base_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    date_today = date.today()
    return  os.path.join(base_path, f"data/raw_data/{city}_{state}_{date_today}.jsonl")
    
if __name__ == "__main__":
    with open('cities.txt','r') as f: 
        contents = f.readlines()

    task = run_for_all_cities(contents)
    task.addBoth(lambda _: reactor.stop())
    reactor.run()


    
        
    

