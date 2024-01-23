from selenium import webdriver 
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
 
import sys
import os
import logging
import time
import csv


SITE_HOME = "https://www.apartments.com/"

class Apartment_Scraper: 

    def __init__(self,location):
        self.delay = .25
        self.location = location
    
    def setup(self):
        # Add basic runtime arguments for driver
        opts = webdriver.ChromeOptions()
        opts.add_argument('--no-sandbox')
        opts.add_argument('--disable-gpu')
        # opts.add_argument('--headless')

        # Adjust dev environment for POSIX environments
        if os.name == 'posix':
            logging.info('POSIX system detected, applying additional DevTool configs')
            opts.add_argument('--remote-debugging-port=9222')
            opts.add_argument('--disable-dev-shm-using')

        # Instantiate webdriver
        self.driver = webdriver.Chrome(options=opts)
        self.driver.get(SITE_HOME)
        

    def adjust_site_settings(self):

        location_input = self.driver.find_element(By.CSS_SELECTOR,'.quickSearchLookup')
        location_input.send_keys(self.location)
        time.sleep(1)
        self.driver.find_element(By.CSS_SELECTOR,'#quickSearch > div > fieldset > div > button').click()
        time.sleep(1)
        self.driver.fullscreen_window()
        time.sleep(1)

        housing_type_drop = self.driver.find_element(By.CSS_SELECTOR,'#type-selection-wrapper > div')
        housing_type_drop.click()
        self.driver.find_element(By.CSS_SELECTOR,'#\30 ')
        housing_type_drop.click()

    def main(self):
        self.setup()
        self.adjust_site_settings()

if __name__ == "__main__":
    # input_location = input('What location would you like to get apartment information from:')
    input_location = 'austin'
    af = Apartment_Scraper(input_location)
    af.main()
        


 