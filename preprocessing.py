import pandas as pd
import os
import json  

class Preprocessing:
    def __init__(self, city, state):
        # Construct the file path for the JSONL (JSON Lines) file
        data_path = os.path.join("data", f"{city}_{state}", f"{city}_{state}_units.jsonl")
        
        # Open and read the file
        with open(data_path, 'r') as file:
            data = file.readlines()
        
        # Create a DataFrame from the data
        self.units_df = self.create_units_df(data)  

    def create_units_df(self, data):
        # Parse each line as a JSON object and collect them into a list
        parsed_data = [json.loads(line.strip()) for line in data if line.strip()]
        
        # Load the list of dictionaries into a DataFrame and return it
        return pd.DataFrame(parsed_data)

    def main(self):
        self.units_df = self.units_df.drop_duplicates()

        # Drop rows with NaN values in critical columns or fill them with a default value
        # Here, we're dropping rows where 'SquareFootage' is NaN. You can also use fillna() if you prefer to fill NaN values instead of dropping them
        self.units_df = self.units_df.dropna(subset=['SquareFootage'])

        # Ensure SquareFootage is a string, handle None values, replace commas, and convert to integers
        self.units_df['SquareFootage'] = self.units_df['SquareFootage'].apply(
            lambda x: int(x.replace(',', '')) if x is not None and isinstance(x, str) else x
        )

        # Save the cleaned DataFrame to a CSV file
        self.units_df.to_csv('test.csv', index=False)

if __name__ == '__main__':
    city, state = 'austin', 'tx'
    pp = Preprocessing(city, state)
    pp.main()