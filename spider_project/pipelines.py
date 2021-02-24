# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import json
import os

class SpiderProjectPipeline:
    def process_item(self, item, spider):
        # print(item)
        dir_name = "./data/" + item["search_word"] + "/extract_json"
        if os.path.exists(dir_name) is False:
            os.makedirs(dir_name)
        file = open(dir_name + "/" + item["id"] + ".json", "w")
        json.dump(item, file, ensure_ascii=False)
        file.close()
        return item


