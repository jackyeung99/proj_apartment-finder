import sqlite3 
import os 
import pandas as pd
import json
from scripts.state_abbreviations import ABBR_TO_NAME
from scripts.json_parser import ApartmentParser, ZillowParser, CityParser

class dataloader:
    def __init__(self, data_dir = 'data/raw_data'):
        self.conn = sqlite3.connect('apf.db')
        self.cur = self.conn.cursor()
        self.cur.execute("PRAGMA foreign_keys = ON")
        self.data_dir = data_dir


#  --------- helpers ---------
    def retrieve_data_files(self):
        return [os.path.join(self.data_dir, f) for f in os.listdir(self.data_dir) if f.endswith('.jsonl')]
    
    def get_city_id(self, city_name, state_name):
        self.cur.execute("SELECT CityId FROM City WHERE CityName = ? AND State = ?", (city_name, state_name))
        result = self.cur.fetchone()
        return result[0] if result else None
    
    def insert_city(self,city_tuple): 
        self.cur.execute('INSERT INTO City(CityName, State, Population, Population_change, Population_males, Population_Females, Median_Resident_Age, Income_2022, Income_2020, per_capita_income_2022, per_capita_income_2020, Median_house_value_2022, Median_house_value_2020, Median_Gross_Rent_2022, Cost_of_living, Poverty_Percentage, Land_area, Population_Density, Tax_with_mortgage, Tax_no_mortgage, Unemployment) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',city_tuple)

    def insert_crime(self, crime_tuple):
        self.cur.execute('INSERT INTO City_Crime(CityId, Year, Murders, Rapes, Robberies, Assaults, Burglaries, Thefts, Auto_thefts, Arson) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', crime_tuple)

    def insert_complex(self,apartment_tuple):
        self.cur.execute('INSERT INTO ApartmentComplex(CityId, WebsiteId, Name, BuildingUrl, Latitude, Longitude, PriceMin, PriceMax, Address, Neighborhood, Zipcode, NumUnits, Source) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', apartment_tuple)
    def insert_units(self, units):
        self.cur.execute(' INSERT INTO ApartmentUnit(BuildingId,WebsiteId,MaxRent,ModelName,Beds,Baths,SquareFootage,Details) VALUES (?,?,?,?,?,?,?,?)',units)

    def insert_amenities(self, amenities): 
        self.cur.execute(' INSERT INTO Unit-Amenities(Unit_Id,CommunityAmmenities) VALUES (?,?)', amenities)

    def source_checker(self, file):
        if 'city_data' in file.lower():
            return 'cities'
        elif 'zillow' in file.lower():
            return 'zillow'
        elif 'apartments' in file.lower():
            return 'apartments' 
        else: 
            raise ValueError('unknown source')
        
    def process_file(self, file):
        #     file_path = os.path.join(self.base_path, file)
        file_path = os.path.join(self.base_path, 'apartments_austin_tx_2024-03-20.jsonl')
        source = self.source_checker(file)
        with open(file_path,'r') as f:
            first_line = json.loads(f.readline())['apartment_json']
            file_state = ABBR_TO_NAME[first_line['listingState']]
            file_city = first_line['listingCity']
            self.get_city_id(file_city,file_state)
            if source == 'cities':
                self.load_cities(file)
            else: 
                self.load_apartments(file, source)
                

    def load_apartments(self,apartment_json, city_id, type):
        if type =='apartments':
            parser = ApartmentParser(apartment_json)
        else:
            parser = ZillowParser(apartment_json)
        for row in apartment_json: 
            apartment_data, units = parser.apartment_parser(row,city_id)
            buildingid  = self.insert_complex(apartment_data)
            unit_data, amenities = parser.unit_parser(units,buildingid)
            unit_id = self.insert_units(unit_data)
            amenity_data = parser.amenity_parser(amenities, unit_id) 


    def load_cities(self,city_json):
        parser = CityParser(city_json)
        for row in city_json: 
            apartment_data, units = parser.apartment_parser(row)
            buildingid  = self.insert_complex(apartment_data)
            unit_data, amenities = parser.unit_parser(units,buildingid)


    def batch_inserts(self):
        for file_path in self.retrieve_data_files():
            self.process_file(file_path)
            self.conn.commit()
    
    def __del__(self):
        self.conn.close()


if __name__ == "__main__":
    loader = dataloader()
    loader.batch_inserts()

        