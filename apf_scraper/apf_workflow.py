import subprocess
import sys
import time
import logging


def run_spiders(city, state):
    start = time.time()
    # Run LinkSpider to scrape links
    subprocess.run(['scrapy', 'crawl', 'apf_crawler', '-a', f'city={city}', '-a', f'state={state}'])
    logging.info('Crawler Finished')
    print('crawler finished')
    # Run apf_parser_Spider to parse links and save data
    subprocess.run(['scrapy', 'crawl', 'apf_parser', '-a', f'city={city}', '-a', f'state={state}'])
    logging.info('Parser Finished')
    end = time.time()
    print(f"runtime: {end-start}")
    
if __name__ == "__main__":
    city = sys.argv[1]
    state = sys.argv[2]
    run_spiders(city, state)