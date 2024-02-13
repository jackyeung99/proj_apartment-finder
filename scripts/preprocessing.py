from sklearn.preprocessing import LabelEncoder
import pandas as pd
import os
from ast import literal_eval

class Preprocessing:
    # FIX ME:
    #  handle files and df in the main processing workflow 
    def __init__(self, units_path, general_info_path):
        # Load data into DataFrames with error handling
        try:
            self.units = pd.read_csv(units_path)
            self.gen_info = pd.read_csv(general_info_path)
        except FileNotFoundError as e:
            raise Exception(f"File not found: {e}")

    def clean_sq_foot_column(self):
        self.units['SquareFootage'] = self.units['SquareFootage'].str.replace(',', '').astype(int, errors='ignore')
        self.units.dropna(subset=['SquareFootage', 'MaxRent'], inplace=True)

    def encode_categories(self):
        # encode categorical data 
        self.gen_info['Neighborhood_Label'] = LabelEncoder().fit_transform(self.gen_info['Neighborhood'])
        self.gen_info['VerifiedListing'] = (self.gen_info['VerifiedListing'] == 'Verified Listing').astype(int)
        self.gen_info['ReviewScore'] = self.gen_info['ReviewScore'].replace("No reviews", 0).astype(float)

    def process_amenities(self):
        self.gen_info['Amenities'] = self.gen_info['Amenities'].apply(self.clean_amenities)

    @staticmethod
    def clean_amenities(amenities):
        if isinstance(amenities, str):
            amenities = literal_eval(amenities)
        return [amenity.replace('*', '').lower() for amenity in amenities]

    def process_data(self):
        self.clean_sq_foot_column()
        self.encode_categories()
        self.process_amenities()

    def save_processed_data(self, output_path):
        final_df = pd.merge(self.gen_info, self.units, on='PropertyId', how='left')
        final_df.to_csv(output_path, index=False)
        print(final_df.head(10))

if __name__ == '__main__':
    base_path = "data"
    for city, state in [('san-diego', 'ca'), ('new-york', 'ny'), ('miami', 'fl'), ('portland', 'or')]:
        units_path = os.path.join(base_path, f"{city}_{state}", f"{city}_{state}_units.csv")
        gen_info_path = os.path.join(base_path, f"{city}_{state}", f"{city}_{state}_info.csv")
        output_path = os.path.join(base_path, "processed_data", f"{city}_{state}_processed.csv")

        pp = Preprocessing(units_path, gen_info_path)
        pp.process_data()
        pp.save_processed_data(output_path)