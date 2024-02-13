from preprocessing import Preprocessing
from geocoder import GeoCoder
from models.nlp_amenities import nlp_processor
from ast import literal_eval
import pandas as pd

class ProcessWorkflow:
    def __init__(self, city, state):
        self.city = city
        self.state = state
        self.nlp = nlp_processor()
        self.geo = GeoCoder()
        self.pre = Preprocessing(city, state)


# ========== Workflow ==========
    def process_data(self):
        self.pre.clean_sq_foot_column()
        self.pre.encode_categories()
        self.process_amenities()
        self.process_addresses()

# ========== Functions ==========
    def process_addresses(self):
        self.pre.gen_info[['Latitude', 'Longitude']] = self.pre.gen_info['Address'].apply(
            lambda x: pd.Series(self.geo.geocode_address(f"{x}, {self.city}, {self.state}"))
        )

    def process_amenities(self):
        self.pre.gen_info['Amenities_Vector'] = self.pre.gen_info['Amenities'].apply(self.nlp.convert_amenities_to_vector)
        self.expand_vectors()

    def expand_vectors(self):
        vector_df = pd.DataFrame(self.pre.gen_info['Amenities_Vector'].tolist())
        vector_df.columns = [f'Feature_{i}' for i in range(vector_df.shape[1])]
        self.pre.gen_info = pd.concat([self.pre.gen_info, vector_df], axis=1).drop('Amenities_Vector', axis=1)