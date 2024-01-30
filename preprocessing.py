import pandas as pd
import os
import json  

class Preprocessing:

    def __init__(self, city, state):
        data_path = os.path.join("data", f"{city}_{state}", f"{city}_{state}.json")
        with open(data_path, 'r') as file:  
            data = json.load(file)  
        self.units_df = pd.json_normalize(data, 'Units') 
        self.create_df(data)  

    def create_df(self, data):
        # Add other property details as new columns with repeated values
        self.units_df['PropertyName'] = data['PropertyName']
        self.units_df['PropertyUrl'] = data['PropertyUrl']
        self.units_df['Address'] = data['Address']
        self.units_df['NeighborhoodLink'] = data['NeighborhoodLink']
        self.units_df['Neighborhood'] = data['Neighborhood']
        self.units_df['ReviewScore'] = data['ReviewScore']
        self.units_df['VerifiedListing'] = data['VerifiedListing']
        # Convert 'Amenities' list into a string and add as a new column
        self.units_df['Amenities'] = ', '.join(data['Amenities'])

    def main(self):
        print(self.units_df.head(30))  # Use print() to display the DataFrame

if __name__ == '__main__':
    city, state = 'austin', 'tx'
    pp = Preprocessing(city, state)
    pp.main()