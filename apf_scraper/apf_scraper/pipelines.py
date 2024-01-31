# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import json
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
        self.file = open(self.file_path, 'a', encoding='utf-8')
        self.first_item = True  # Add a flag to check for the first item

    def close_spider(self, spider):
        # Close the JSON array if necessary
        if not self.first_item:
            self.file.write(']\n')  # Close the JSON array
        self.file.close()

    def process_item(self, item, spider):
        if item.__class__.__name__ == self.item_class_name:
            if self.first_item:
                self.file.write('[')  # Start the JSON array
                self.first_item = False
            else:
                self.file.write(',\n')  # Add a comma before the next item, except for the first
            line = json.dumps(dict(item), ensure_ascii=False)
            self.file.write(line)
        return item


class ApartmentGeneralInfoPipeline(BasePipeline):
    item_class_name = 'ApfGeneralInfoItem'
    file_name_suffix = 'info.jsonl'  

class UnitPricesPipeline(BasePipeline):
    item_class_name = 'ApfUnitItem'
    file_name_suffix = 'units.jsonl'