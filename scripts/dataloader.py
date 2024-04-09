import sqlite3 
import os 

import json
from utils.database_manager import DatabaseManager
from utils.json_parser import  CityParser, ZillowParser, ApartmentParser


class dataloader:
    def __init__(self, data_dir = 'data/raw_data'):
        self.db_manager = DatabaseManager(db_path='apf.db')
        self.data_dir = data_dir
        self.source_to_method = {
            'city_data': self.load_cities,
            'zillow': self.load_zillow,
            'apartments': self.load_apartments
        }

    def retrieve_data_files(self):
        return [os.path.join(self.data_dir, f) for f in os.listdir(self.data_dir) if f.endswith('.jsonl')]
    
    def parse_filename(self, filename):
        """
        Extracts city and state information from the file name.
        Assumes format like 'zillow_portland_or_2024-03-30.jsonl'
        """
        name_without_extension = os.path.splitext(filename)[0] 
        parts = name_without_extension.split('_')  # Split by underscore
     
        city = parts[-3].title().replace('-',' ')
        state_abbr = parts[-2].upper()  
        return city, state_abbr

    def process_file(self, file_path):
        source = None
        for key in self.source_to_method.keys():
            if key in file_path.lower():
                source = key
                break
        
        if source:
            processing_method = self.source_to_method[source]
            processing_method(file_path)
        else:
            raise ValueError('Unknown source for file:', file_path)
         
            
    def load_zillow(self, file_path):
        city, state_abbr = self.parse_filename(file_path)
        city_id = self.db_manager.get_city_id(city,state_abbr)
        with self.db_manager, open(file_path, 'r') as f:
            
            for row in f: 

                apartment_json = json.loads(row)['apartment_json']

                parser = ZillowParser()
                
                apartment_data, units = parser.parse(apartment_json,city_id)

                # buildingid  = self.db_manager.insert_complex(apartment_data)
             
                amenity_data = parser.parse_ammenity(apartment_json) 
                print(amenity_data)
                # self.db_manager.insert_amenities(amenity_data, unit_id)

    def load_apartments(self,file_path):
        city, state_abbr = self.parse_filename(file_path)
        city_id = self.db_manager.get_city_id(city,state_abbr)
        with self.db_manager, open(file_path, 'r') as f:
            for row in f: 
                
                apartment_json = json.loads(row)['apartment_json']
        
                parser = ApartmentParser()

                apartment_data, units = parser.parse(apartment_json,city_id)
            
                # # buildingid  = self.db_manager.insert_complex(apartment_data)
                # # unit_id = self.db_manager.insert_units(unit_data)
                amenity_data = parser.parse_amenities(apartment_json) 
                # print(amenity_data)
                # self.db_manager.insert_amenities(amenity_data,unit_id)


    def load_cities(self,file_path):
        with self.db_manager, open(file_path, 'r') as f:
            for line in f:
                city_json = json.loads(line)

                parser = CityParser()
                city_data, crimes = parser.city_parser(city_json)
                city_id = self.db_manager.insert_city(city_data)
        
                for crime_data in crimes:
                    crime_data.CityId = city_id
                    self.db_manager.insert_crime(crime_data)

    def batch_inserts(self):
        for file_path in self.retrieve_data_files():
            if 'zillow' in file_path:
                try: 
                    self.process_file(file_path)
                except ValueError as e:
                    print(e)
                break
                



if __name__ == "__main__":
    loader = dataloader()

    loader.batch_inserts()

        