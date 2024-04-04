import sqlite3 
import os 
import pandas as pd
import json





class dataloader:
    def __init__(self):
        self.conn = sqlite3.connect('apf.db')
        self.cur = self.conn.cursor()
        self.files = self.retrieve_data()

    def retrieve_data(self):
        dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        self.base_path = os.path.join(dir_path,'data/raw_data')
        files = os.listdir(self.base_path)
        return files

    def process_batch(self,batch_lines,type):
        for city in batch_lines: 
            sub_json = json.loads(city)
            method_name = f'load_{type}'
            process_method = getattr(self, method_name, None)
            if process_method:
                process_method(sub_json)

        
                
    def batch_inserts(self):
        # Read the JSONL file in batches and process each batch
        batch_size = 100
            # check file type 
        for file in self.files: 
            print(f"Processing: {file}")
            if 'city_data' in file.lower():
                type = 'cities'
            elif 'zillow' in file.lower():
                type = 'zillow'
            elif 'apartments' in file.lower():
                type = 'apartments' 
                
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


            

    # loading different file types and tables 
    def load_apartments(self, apartment_json):
        # apartments = [(
        # )for apartment in apartment_json]
        # self.cur.execute('INSERT INTO apartments (listingId, listingCity, ...) VALUES (?, ?, ...)', data)
        # self.conn.commit()
        pass


    def load_zillow(self,apartment_json):
        pass


    def load_cities(self, city):
        city_tuple = (city['city'], 
                    city['state'],
                    city['population'],
                    city['population_change'],
                    city['males'],
                    city['females'],
                    city['median_resident_age'],
                    city['median_household_income_2022'],
                    city['median_household_income_2000'],
                    city['per_capita_income_2022'],
                    city['per_capita_income_2000'],
                    city['median_house_value_2022'],
                    city['median_house_value_2000'],
                    city['median_gross_rent'],
                    city['cost_of_living_index'],
                    city['poverty_percentage'],
                    city['land_area'],
                    city['population_density(per square mile)'],
                    city['tax_percentage_with_mortgage'],
                    city['tax_percentage_no_mortgage'],
                    city['unemployment_rate'])
        
        print(city_tuple)
        
        self.cur.execute('INSERT INTO City(CityName, State, Population, Population_change, Population_males, Population_Females, Median_Resident_Age, Income_2022, Income_2020, per_capita_income_2022, per_capita_income_2020, Median_house_value_2022, Median_house_value_2020, Median_Gross_Rent_2022, Cost_of_living, Poverty_Percentage, Land_area, Population_Density, Tax_with_mortgage, Tax_no_mortgage, Unemployment) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',city_tuple)

        city_id = self.cur.lastrowid
        for year in city.get('crime', []):
            crime_tuple = (city_id,
                            year['year'],
                            year['Murders'],
                            year['Rapes'],
                            year['Robberies'],
                            year['Assaults'],
                            year['Burglaries'],
                            year['Thefts'],
                            year['Auto thefts'],
                            year['Arson']
                            )
            self.cur.execute('INSERT INTO City_Crime(CityId, Year, Murders, Rapes, Robberies, Assaults, Burglaries, Thefts, Auto_thefts, Arson) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', crime_tuple)

        self.conn.commit()
        
        def __del__(self):
            self.conn.close()


if __name__ == "__main__":
    loader = dataloader()
    loader.batch_inserts()

        