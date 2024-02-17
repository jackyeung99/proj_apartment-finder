from preprocessing import Preprocessing
from geocoder import GeoCoder
from ast import literal_eval
import pandas as pd
import os
import sys 

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from models.nlp_amenities import nlp_processor


class ProcessWorkflow:
    def __init__(self):
        self.nlp = nlp_processor()
        self.geo = GeoCoder(max_workers=10)
        
# ========== main workflow ==========
    def process_data(self, city, state):
        """Process data for a given city and state."""
        units_path, info_path = self.construct_file_paths(city, state)
        units_df, gen_info_df = self.load_data(units_path, info_path)
    
        if '-' in city:
            split = city.split('-')
            self.city_str = ' '.join(split) 
        else:
            self.city_str = city

        pre = Preprocessing(units_df, gen_info_df)
        df = pre.process_data()
        # self.process_amenities(df)
        self.process_addresses(df)
        return df

# ========== load data  ==========
    def construct_file_paths(self, city, state):
        """Retrieve file paths given city and state"""
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        units_path = os.path.join(base_path,'data', f'{city}_{state}', f'{city}_{state}_units.csv')
        info_path = os.path.join(base_path ,'data', f'{city}_{state}', f'{city}_{state}_info.csv')
        return units_path, info_path

    def load_data(self, units_path, info_path):
        """Load units and general info DataFrames from specified paths."""
        units_df = pd.read_csv(units_path)
        gen_info_df = pd.read_csv(info_path)
        return units_df, gen_info_df
    
# ========== scripts ==========
    def process_addresses(self, df):
        """Geocode addresses and update the DataFrame with 'Latitude' and 'Longitude'."""
        full_addresses = [f"{addr}, {self.city_str}, {state}" for addr in df['Address'].unique()]
        results = self.geo.batch_geocode(full_addresses)
        coords = []
        for addr in full_addresses:
            lat, lon = results.get(addr, (None, None))
            coords.append((lat, lon))

        # Update the DataFrame with the latitude and longitude values
        df[['Latitude', 'Longitude']] = pd.DataFrame(coords, columns=['Latitude', 'Longitude'], index=df.index)

    def process_amenities(self, df):
        """Vectorize amenities and expand them into separate columns in the DataFrame."""
        df['Amenities_Vector'] = df['Amenities'].apply(self.nlp.convert_amenities_to_vector)
        vector_df = pd.DataFrame(df['Amenities_Vector'].tolist())
        vector_df.columns = [f'Feature_{i}' for i in range(vector_df.shape[1])]
        df.drop('Amenities_Vector', axis=1, inplace=True)
        df = pd.concat([df, vector_df], axis=1)

if __name__ == '__main__':
    
    locations = [('austin', 'tx'), ('san-diego', 'ca'), ('new-york', 'ny'),('san-francisco','ca'),('seattle','wa'),('portland','or'),('los-angeles','ca'),('chicago','il'),('miami','fl')]
    workflow = ProcessWorkflow()

    for city, state in locations:
        df = workflow.process_data(city, state)
        output_path = os.path.join('data', 'processed_data', f'{city}_{state}_processed.csv')
        df.to_csv(output_path, index=False)
        print(df.head(10))
        print(f'processed {city} {state}')
    