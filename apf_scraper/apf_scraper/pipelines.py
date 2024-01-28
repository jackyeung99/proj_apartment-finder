# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import json

class ApfScraperPipeline:
    def __init__(self):
        self.items_buffer = []

    def open_spider(self, spider):
        self.file = open(spider.output_file_path, 'w')
        self.file.write('[')

    def close_spider(self, spider):
        if self.items_buffer:
            self.file.write('\n' + ',\n'.join(self.items_buffer))
        self.file.write('\n]')
        self.file.close()

    def process_item(self, item, spider):
        if spider.name != "apf_parser":
            return item

        line = json.dumps(dict(item), ensure_ascii=False, indent=4)
        self.items_buffer.append(line)

        # Write buffer to file if it reaches a certain size
        if len(self.items_buffer) >= 10:  # Adjust the buffer size as needed
            self.file.write('\n' + ',\n'.join(self.items_buffer) + ',')
            self.items_buffer = []

        return item