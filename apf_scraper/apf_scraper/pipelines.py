# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
import json
import csv
import os

class LinkPipeline:
    def open_spider(self, spider):
        self.base_dir = f"../data/{spider.city}_{spider.state}"
        os.makedirs(self.base_dir, exist_ok=True)
        # Change the file extension to .txt
        self.file_path = os.path.join(self.base_dir, f'{spider.city}_{spider.state}_links.txt')
        self.file = open(self.file_path, 'w', encoding='utf-8')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        if item.__class__.__name__ == 'ApfScraperLinkItem':
            # Write the link directly followed by a newline character instead of JSON formatting
            self.file.write(item['PropertyUrl'] + '\n')
            return item
        
class BasePipeline:
    def open_spider(self, spider):
        # Dynamically set the file name using spider attributes
        self.file_name = f'{spider.city}_{spider.state}_{self.file_name_suffix}'
        self.file_path = f'../data/{spider.city}_{spider.state}/{self.file_name}'
        self.buffer = []  
        self.batch_size = 50
        self.file = open(self.file_path, 'w', newline='', encoding='utf-8')
        self.writer = None

    def close_spider(self, spider):
        self.flush_buffer() 
        self.file.close()

    def process_item(self, item, spider):
        if item.__class__.__name__ == self.item_class_name:
            self.buffer.append(ItemAdapter(item).asdict())  # Add item to buffer
            if len(self.buffer) >= self.batch_size:
                self.flush_buffer()  # Write buffered items to file when batch size is reached
        return item

    def flush_buffer(self):
        if not self.writer:
            # Initialize the CSV writer and write the header if it's the first batch
            self.writer = csv.DictWriter(self.file, fieldnames=self.buffer[0].keys())
            self.writer.writeheader()
        self.writer.writerows(self.buffer)  # Write all buffered items to the file
        self.buffer.clear() 
        self.file = open(self.file_path, 'w', newline='', encoding='utf-8')
        self.writer = None  # Initialize the CSV writer

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        if item.__class__.__name__ == self.item_class_name:
            if not self.writer:
                self.writer = csv.DictWriter(self.file, fieldnames=item.fields.keys())
                self.writer.writeheader()  
            self.writer.writerow(dict(item))  
        return item

class ApartmentGeneralInfoPipeline(BasePipeline):
    item_class_name = 'ApfGeneralInfoItem'
    file_name_suffix = 'info.csv'

class UnitPricesPipeline(BasePipeline):
    item_class_name = 'ApfUnitItem'
    file_name_suffix = 'units.csv'