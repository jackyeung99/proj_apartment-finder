from sklearn.preprocessing import LabelEncoder
from models.nlp_amenities import nlp_processor
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import pandas as pd
import os
import ast 

class Preprocessing:
    def __init__(self, city, state):
        # Set city and state
        self.city = city
        self.state = state

        # Construct file paths for unit and general information CSV files
        units_path = os.path.join("data", f"{city}_{state}", f"{city}_{state}_units.csv")
        general_info_path = os.path.join("data", f"{city}_{state}", f"{city}_{state}_info.csv")

        # Load data into DataFrames
        self.units = pd.read_csv(units_path)
        self.gen_info = pd.read_csv(general_info_path)

        # Initialize NLP processor
        self.nlp_processor = nlp_processor()
        
# ============== Unit preprocessing ============== 
    def clean_sq_foot_column(self):
        # Drop rows with missing values in 'SquareFootage' and 'MaxRent', and convert 'SquareFootage' to int
        self.units.dropna(subset=['SquareFootage', 'MaxRent'], inplace=True)
        self.units['SquareFootage'] = self.units['SquareFootage'].str.replace(',', '').astype(int)
        

# ============== Gen info preprocessing ============== 
    def encode_categories(self):
        # Convert categorical data such as 'Neighborhood' into integers
        label_encoder = LabelEncoder()
        self.gen_info['Neighborhood_Label'] = label_encoder.fit_transform(self.gen_info['Neighborhood'])
        self.gen_info['VerifiedListing'] = self.gen_info['VerifiedListing'].apply(lambda x: 1 if x == 'Verified Listing' else 0)

    def process_amenities(self):
        # Convert amenities from string representations to lists, clean up, and convert to vectors
        self.gen_info['Amenities'] = self.gen_info['Amenities'].apply(ast.literal_eval)
        self.gen_info['Amenities'] = self.gen_info['Amenities'].apply(
            lambda amenities_list: [amenity.replace('*', '').lower() for amenity in amenities_list]
        )
        self.gen_info['Amenities_Vector'] = self.gen_info['Amenities'].apply(
            lambda x: self.nlp_processor.convert_amenities_to_vector(x)
        )

    def geocode_address(self, address, attempt=1, max_attempts=3):
        geolocator = Nominatim(user_agent="my_geocoder")
        try:
            # Increase timeout to, e.g., 10 seconds
            location = geolocator.geocode(address, timeout=10)
            if location:
                return location.latitude, location.longitude
            else:
                return None, None
        except (GeocoderTimedOut, GeocoderUnavailable) as e:
            if attempt <= max_attempts:
                print(f"Geocoding attempt {attempt} failed, retrying...")
                return self.geocode_address(address, attempt + 1, max_attempts)
            else:
                print(f"Geocoding failed after {max_attempts} attempts.")
                return None, None  # retry on timeout

    # Note: Takes a considerable amount of time to convert addresses due to api request limits
    def process_addresses(self):
        # Add columns for latitude and longitude
        self.gen_info['Latitude'] = None
        self.gen_info['Longitude'] = None

        # Iterate over the DataFrame and geocode each address
        for index, row in self.gen_info.iterrows():
            lat, lon = self.geocode_address(row['Address'])
            self.gen_info.at[index, 'Latitude'] = lat
            self.gen_info.at[index, 'Longitude'] = lon

    def main(self):
        # Process data
        self.clean_sq_foot_column()
        self.encode_categories()
        self.process_amenities()
        self.process_addresses()
        # Merge DataFrames and prepare the final DataFrame for analysis
        final_df = pd.merge(self.gen_info, self.units, on='PropertyId', how='left')
        final_df = final_df[['PropertyId','Latitude','Longitude','ReviewScore', 'Neighborhood_Label', 'Amenities_Vector', 'Baths', 'Beds', 'MaxRent', 'SquareFootage']].dropna()
        final_df.to_csv(f'data/processed_data/{self.city}_{self.state}_processed.csv', index=False)
        # # Display the prepared DataFrame
        pd.set_option('display.max_columns', None)
        print(final_df.head(40))

if __name__ == '__main__':
    city, state = 'seattle', 'wa'
    pp = Preprocessing(city, state)
    pp.main()