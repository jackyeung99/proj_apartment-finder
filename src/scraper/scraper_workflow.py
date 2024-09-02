
import os
import sys
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(repo_root)


import asyncio
from twisted.internet import asyncioreactor
asyncioreactor.install(asyncio.get_event_loop())

import time
from datetime import date
from scrapy.crawler import CrawlerRunner
from scrapy.signalmanager import dispatcher
from scrapy import signals 
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings


# import spiders
from src.scraper.apf_scraper.spiders.apf_crawler import ApfCrawlerSpider
from src.scraper.apf_scraper.spiders.apf_parser import ApfParserSpider
# from src.scraper.apf_scraper.spiders.zillow_api import ZillowAPI


''' Run spiders sequentially, while feeding in the data of the crawler spiders into the parsers'''
@defer.inlineCallbacks
def run_spiders_for_city(city, state):
    links = []
    complexes = []

    apartments_file = get_file(city=city,state=state,type='apartments')
    zillow_file = get_file(city=city,state=state,type='zillow')

    settings = get_project_settings()
    configure_logging(settings)
    runner = CrawlerRunner(settings)

    def collect_links(item, response, spider):
        if spider.name == 'apf_crawler':
            links.append(item['url'])

    dispatcher.connect(collect_links, signal=signals.item_scraped)

    yield runner.crawl(ApfCrawlerSpider, city=city, state=state)
    yield runner.crawl(ApfParserSpider, apartments_to_scrape=links, file=apartments_file)
    links.clear()
    # yield runner.crawl(ZillowAPI, city=city, state=state, file=zillow_file)

@defer.inlineCallbacks
def run_for_all_cities(cities):
    start = time.time()
    for location in cities:
        city, state = location.split(',')
        print(city,state)
        yield run_spiders_for_city(city.strip(), state.strip())
    print(f"all cities scraped, total time{time.time()-start}")
   


def get_file(city,state,type):
    date_today = date.today()
    return  os.path.join(repo_root, f"data/raw_data/{type}_{city}_{state}_{date_today}.jsonl")
    
if __name__ == "__main__":
    with open('cities.txt','r') as f: 
        contents = f.readlines()

    task = run_for_all_cities(contents)
    task.addBoth(lambda _: reactor.stop())
    reactor.run()


    
        
    

