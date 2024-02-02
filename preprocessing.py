from sklearn.preprocessing import LabelEncoder
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from concurrent.futures import ThreadPoolExecutor
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import pandas as pd
import os
import time
import json  
import ast

class Preprocessing:
    def __init__(self, city, state):
        self.city = city
        self.state = state
        # Construct the file path for the JSONL (JSON Lines) file
        units_path = os.path.join("data", f"{city}_{state}", f"{city}_{state}_units.csv")
        general_info = os.path.join("data",f"{city}_{state}", f"{city}_{state}_info.csv")
        # Create a DataFrame from the data
        units = pd.read_csv(units_path)
        gen_info = pd.read_csv(general_info)  
        self.main_data = main = pd.merge(gen_info, units, on='PropertyId', how='left').drop_duplicates()
        
    def clean_sq_foot_column(self):
        self.main_data = self.main_data.dropna(subset=['SquareFootage','MaxRent'])
        self.main_data['SquareFootage'] = self.main_data['SquareFootage'].str.replace(',', '').astype(int)
        
    def encode_categories(self):
        ''' represent categorical data such as neighborhoods into int'''
        label_encoder = LabelEncoder()
        self.main_data['Neighborhood_Label'] = label_encoder.fit_transform(self.main_data['Neighborhood'])
        self.main_data['VerifiedListing'] = self.main_data['VerifiedListing'].apply(lambda x: 1 if x == 'Verified Listing' else 0)

    # def geocode_address(self, address, attempts=3, delay=1):
    #     geolocator = Nominatim(user_agent="geoapiExercises")
    #     for attempt in range(attempts):
    #         try:
    #             location = geolocator.geocode(f"{address},{self.city},{self.state}")
    #             return (location.latitude, location.longitude) if location else (None, None)
    #         except (GeocoderTimedOut, GeocoderServiceError) as e:
    #             if attempt < attempts - 1:  # If not the last attempt, wait before retrying
    #                 time.sleep(delay)
    #                 continue
    #             else:
    #                 return None, None 


    def main(self):
        self.clean_sq_foot_column()
        self.encode_categories()
        
        pd.set_option('display.max_columns', None)

        # Now, when you call df.head(), it will display all columns
        print(self.main_data.head())

if __name__ == '__main__':
    city, state = 'austin', 'tx'
    pp = Preprocessing(city, state)
    pp.main()