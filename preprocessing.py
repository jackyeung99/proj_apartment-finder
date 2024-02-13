from sklearn.preprocessing import LabelEncoder
from models.nlp_amenities import nlp_processor
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import pandas as pd
import os
import ast 
from ast import literal_eval

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
        self.gen_info['ReviewScore'] = self.gen_info['ReviewScore'].apply(
            lambda x: 0 if x == "No reviews" else float(x)
        )

    def process_amenities(self):
        # Process 'Amenities' in place, avoiding repeated 'apply'
        self.gen_info['Amenities'] = self.gen_info['Amenities'].apply(lambda x: self.clean_and_vectorize_amenities(x))
        self.expand_vectors()

    def clean_and_vectorize_amenities(self, amenities):
        if isinstance(amenities, str):
            amenities = literal_eval(amenities)
        cleaned_amenities = [amenity.replace('*', '').lower() for amenity in amenities]
        return self.nlp_processor.convert_amenities_to_vector(cleaned_amenities)

    def expand_vectors(self):
        # Assuming 'Amenities_Vector' is now a list of vectors
        expanded_df = self.gen_info['Amenities'].apply(pd.Series)
        labels = ['Leisure', 'Technology', 'Services', 'Location', 'Fitness & Wellness', 'Safety & Security', 'Apartment_features', 'Appliances']
        # Use meaningful labels if they match the vector size
        if len(labels) == expanded_df.shape[1]:
            expanded_df.columns = labels
        else:
            expanded_df.columns = [f'Vector_{i+1}' for i in expanded_df.columns]

        # Merge expanded vectors back into the main DataFrame
        self.gen_info = pd.concat([self.gen_info.drop('Amenities', axis=1), expanded_df], axis=1)

    def geocode_address(self, address, attempt=1, max_attempts=3):
        geolocator = Nominatim(user_agent="my_geocoder")
        try:
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
            lat, lon = self.geocode_address(row['Address'] + f',{self.city},{self.state}')
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
        final_df = final_df[['PropertyId','Latitude','Longitude','ReviewScore', 'Neighborhood_Label', 'Leisure', 'Technology', 'Services', 'Location', 'Fitness & Wellness', 'Safety & Security', 'Apartment_features', 'Appliances', 'Baths', 'Beds', 'MaxRent', 'SquareFootage']].dropna()
        final_df.to_csv(f'data/processed_data/{self.city}_{self.state}_processed.csv', index=False)
        # # Display the prepared DataFrame
        pd.set_option('display.max_columns', None)
        print(final_df.head(10))

if __name__ == '__main__':
    cities = [('san-diego','ca'),('new-york','ny'),('miami','fl'),('portland','or')]
    for city in cities:
        pp = Preprocessing(city[0], city[1])
        pp.main()