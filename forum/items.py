# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

    
class PostItemsList(scrapy.Item):
    author = scrapy.Field()
    author_link = scrapy.Field()
    create_date = scrapy.Field()
    post = scrapy.Field()
    topic=scrapy.Field()
    tag=scrapy.Field()
    url = scrapy.Field()
    condition=scrapy.Field()    
