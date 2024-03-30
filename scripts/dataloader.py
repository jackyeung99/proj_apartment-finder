import sqlite3 
import os 
import pandas as pd
import json


# DATABASE = 'apf.db'
# CONN = sqlite3.connect(DATABASE)


class dataloader:
    def __init__(self):
        self.files = self.retrieve_data()

    def retrieve_data(self):
        dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        self.base_path = os.path.join(dir_path,'data/raw_data')
        files = os.listdir(self.base_path)
        return files

    def process_batch(self,batch_lines,type):
        for apartment in batch_lines:
            apartment = json.loads(apartment)
            method_name = f'load_{type}'
            process_method = getattr(self, method_name, None)
            if process_method:
                process_method(apartment)
            else:
                print(f"No method found for type: {type}")
                

    def batch_inserts(self):
        # Read the JSONL file in batches and process each batch
        batch_size = 100
        for file in self.files: 
            # check file type 
            if 'city_data' in file.lower():
                type = 'cities'
            elif 'zillow' in file.lower():
                type = 'zillow'
            elif 'apartments' in file.lower():
                type = 'apartments' 
            else: 
                type = 'market_trends'


            file_path = os.path.join(self.base_path, file)
            with open(file_path, 'r') as file:
                batch_lines = []
                for line in file:
                    batch_lines.append(line)
                    if len(batch_lines) >= batch_size:
                        self.process_batch(batch_lines,type)
                        batch_lines = [] 
                if batch_lines:  # Process any remaining lines
                    self.process_batch(batch_lines, type) 
            
    def main(self):
        self.batch_inserts()

    # loading different file types and tables 
    def load_apartments(self, apartment_json):
        pass

    def load_zillow(self,apartment_json):
        pass

    def load_market_trends(self, trends_json): 
        pass

    def load_cities(self, city_json):
        pass


if __name__ == "__main__":
    sql = dataloader()
    sql.main()