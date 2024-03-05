
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

    links = ['https://www.apartments.com/club-torrey-pines-san-diego-ca/sdjnx85/', 'https://www.apartments.com/fourth-and-laurel-san-diego-ca/3jn0b4f/', 'https://www.apartments.com/pinnacle-broadway-san-diego-ca/jdfspp5/', 'https://www.apartments.com/sola-san-diego-ca/n0xnw2m/', 'https://www.apartments.com/town-park-villas-senior-apartments-55-san-diego-ca/zgqj3lw/', 'https://www.apartments.com/vora-lux-san-diego-ca/55ets1q/', 'https://www.apartments.com/cresta-bella-san-diego-ca/kmwpnpc/', 'https://www.apartments.com/loma-palisades-san-diego-ca/8tj1ze0/', 'https://www.apartments.com/stanza-little-italy-san-diego-ca/yphefxs/', 'https://www.apartments.com/river-run-village-san-diego-ca/p91mxvr/', 'https://www.apartments.com/la-jolla-nobel-san-diego-ca/37p58vd/', 'https://www.apartments.com/casoleil-san-diego-ca/vye0t0g/', 'https://www.apartments.com/bay-san-diego-ca/bq4wff8/', 'https://www.apartments.com/lux-by-garden-san-diego-ca/2bdptcb/', 'https://www.apartments.com/artisan-san-diego-ca/zd2drxy/', 'https://www.apartments.com/the-courtyards-pacific-village-san-diego-ca/sj3z796/', 'https://www.apartments.com/domain-san-diego-san-diego-ca/m2hvg0h/', 'https://www.apartments.com/la-terraza-apartments-san-diego-ca/517s4bp/', 'https://www.apartments.com/denizen-san-diego-ca/se7fgv7/', 'https://www.apartments.com/k1-apartments-san-diego-ca/d0mqjxh/', 'https://www.apartments.com/the-casas-san-diego-ca/lwlmmrg/']
    # yield runner.crawl(ApfCrawlerSpider, city=city, state=state)
   
    yield runner.crawl(ApfParserSpider, apartments_to_scrape=links, file=file)
    # yield runner.crawl(ZillowCrawlerSpider, city=city, state=state)
    # yield runner.crawl(ZillowParserSpider, apartments_to_scrape=complexes, file=file)
    # print(f"{city} took {time.time()-city_start} to finish scraping")
 
@defer.inlineCallbacks
def run_for_all_cities(cities):
    start = time.time()
    for location in cities[:1]:
        city, state = location.split(',')
        file = get_file(city,state)
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


    
        
    

