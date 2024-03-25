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

    def process_json(self,apartment_object):
        apartment = json.loads(apartment_object)
        print(apartment['apartment_json'].keys())

    def process_batch(self,batch_lines):
        # for apartment in batch_lines[:2]:
        self.process_json(batch_lines[0])

    def batch_inserts(self):
        # Read the JSONL file in batches and process each batch
        batch_size = 100
        for file in self.files[:1]: 
            file_path = os.path.join(self.base_path, file)
            with open(file_path, 'r') as file:
                batch_lines = []
                for line in file:
                    batch_lines.append(line)
                    if len(batch_lines) >= batch_size:
                        self.process_batch(batch_lines)
                        batch_lines = []  # Reset for next batch
                if batch_lines:  # Process any remaining lines
                    self.process_batch(batch_lines) 

    def main(self):
        self.batch_inserts()


if __name__ == "__main__":
    sql = dataloader()
    sql.main()