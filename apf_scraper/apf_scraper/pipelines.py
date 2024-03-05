# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
import json
import os

        
class ApfPipeline:
    def __init__(self):
        self.buffer = [] 
        self.buffer_size = 25

    def open_spider(self, spider):
        if hasattr(spider, 'file') and spider.file is not None:
            self.file = open(spider.file, 'a', encoding='utf-8')
        else:
            self.file = None

    def close_spider(self, spider):
        if self.file:
            self.flush_buffer() 
            self.file.close()

    def process_item(self, item, spider):
        if item.__class__.__name__ == 'Apartment':
            line = json.dumps(dict(item)) + "\n"
            self.buffer.append(line) 
            print(line)
            if len(self.buffer) >= self.buffer_size:  
                self.flush_buffer() 
        return item

    def flush_buffer(self):
        """Write the contents of the buffer to the file and clear the buffer."""
        if self.file and self.buffer:
            self.file.writelines(self.buffer)  
            self.buffer.clear()  