
import asyncio
from twisted.internet import asyncioreactor
asyncioreactor.install(asyncio.get_event_loop())
import time
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

@defer.inlineCallbacks
def run_spiders_for_city(city, state):
    links = []
    complexes = []
    
    settings = get_project_settings()
    configure_logging(settings)
    runner = CrawlerRunner(settings)

    def collect_links(item, response, spider):
        # Assume each item yielded by Spider1 has a 'url' key
        if spider.name == 'apf_crawler':
            links.append(item['url'])
        elif spider.name == 'zillow_crawler':
            complexes.append(item['Geo'])

    dispatcher.connect(collect_links, signal=signals.item_scraped)

    yield runner.crawl(ApfCrawlerSpider, city=city, state=state)
    yield runner.crawl(ApfParserSpider, apartments_to_scrape=links)
    yield runner.crawl(ZillowCrawlerSpider, city=city, state=state)
    yield runner.crawl(ZillowParserSpider, apartments_to_scrape=complexes)
 
@defer.inlineCallbacks
def run_for_all_cities(cities):
    start = time.time()
    for location in cities:
        city, state = location.split(',')
        yield run_spiders_for_city(city.strip(), state.strip())
    print(f"all cities scraped, total time{time.time()-start}")

    
if __name__ == "__main__":
    with open('cities.txt','r') as f: 
        contents = f.readlines()

    task = run_for_all_cities(contents)
    task.addBoth(lambda _: reactor.stop())  # Stop reactor when all tasks are done
    reactor.run()


    
        
    

