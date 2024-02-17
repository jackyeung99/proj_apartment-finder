from sklearn.preprocessing import LabelEncoder
import pandas as pd
import os
from ast import literal_eval

class Preprocessing:

    @staticmethod
    def clean_amenities(amenities):
        if isinstance(amenities, str):
            amenities = literal_eval(amenities)
        return [amenity.replace('*', '').lower() for amenity in amenities]
    
    def __init__(self, units_df, gen_info_df):
        self.units = units_df
        self.gen_info = gen_info_df
    
    def clean_sq_foot_column(self):
        self.units['SquareFootage'] = self.units['SquareFootage'].str.replace(',', '').astype(int, errors='ignore')
        self.units.dropna(subset=['SquareFootage', 'MaxRent'], inplace=True)

    def encode_categories(self):
        # encode categorical data
        self.gen_info['Neighborhood_Label'] = LabelEncoder().fit_transform(self.gen_info['Neighborhood'])
        self.gen_info['VerifiedListing'] = (self.gen_info['VerifiedListing'] == 'verified').astype(int)


    def process_amenities(self):
        self.gen_info['Amenities'] = self.gen_info['Amenities'].apply(self.clean_amenities)

    def process_data(self):
        self.clean_sq_foot_column()
        self.encode_categories()
        self.process_amenities()
        return pd.merge(self.gen_info, self.units, on='PropertyId', how='left')
        

if __name__ == '__main__':
    # test functionality
    units_path = os.path.join('../','data','austin_tx','austin_tx_units.csv')
    info_path = os.path.join('../','data','austin_tx','austin_tx_info.csv')
    units_df = pd.read_csv(units_path)
    gen_info_df = pd.read_csv(info_path)

    pp = Preprocessing(units_df,gen_info_df)
    df = pp.process_data()
    with pd.option_context('display.max_rows',30,'display.max_columns', None): print(df)