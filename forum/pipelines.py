# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exceptions import DropItem
from scrapy import signals
import hashlib
from fluent import sender
from fluent import event

# from scrapy.contrib.exporter import CsvItemExporter

# Pipeline to remove duplicate objects


class AddUUIDPipeline(object):
    def process_item(self,item,spider):
        newStr = item['author']+item['author_link']+item['create_date']+item['message']+item['topic']+item['url']+item['condition']
        item['post_id']= hashlib.md5(newStr).hexdigest()[:9]


# Pipeline to remove duplicate objects
class DuplicatesLinksPipeline(object):
    def __init__(self):
        self.checked_links = set()

    def process_item(self,item,spider):
        check = item['url']

        if check in self.checked_links:
            raise DropItem("Already added %s" % item)
        else:
            self.checked_links.add(check)
            return item 


class FluentdPipeline(object):
    def __init__(self):
        sender.setup('FM')

    # send event to fluentd, with 'app.follow' tag
    def process_item(self,item,spider):
        event.Event('post', {
          'user_id': item['author']
          ,'user_link':item['author_link']
          ,'domain': item['domain']
          ,'post_id': item['post_id']
          ,'@timestamp': item['create_date']
          ,'message':item['post']
          ,'topic':item['topic']
          ,'condition':item['condition']
          ,'url':item['url']
        })

# 
# # Pipeline to make sure CSV columns export in the right order
# class CSVPipeline(object):
# 
#   def __init__(self):
#     self.files = {}
# 
#   @classmethod
#   def from_crawler(cls, crawler):
#     pipeline = cls()
#     crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
#     crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
#     return pipeline
# 
#   def spider_opened(self, spider):
#     file = open('%s.csv' % spider.name, 'w+b')
#     self.files[spider] = file
#     self.exporter = CsvItemExporter(file)
#     self.exporter.fields_to_export = ['brand','name','division','category','price','image_link']
#     self.exporter.start_exporting()
# 
#   def spider_closed(self, spider):
#     self.exporter.finish_exporting()
#     file = self.files.pop(spider)
#     file.close()
# 
#   def process_item(self, item, spider):
#     self.exporter.export_item(item)
#     return item