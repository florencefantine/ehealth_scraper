# -*- coding: utf-8 -*-
import scrapy
import hashlib
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.selector import Selector
from forum.items import PostItemsList
import re
from bs4 import BeautifulSoup
import logging
import string
import dateparser
import time

## LOGGING to file
#import logging
#from scrapy.log import ScrapyFileLogObserver

#logfile = open('testlog.log', 'w')
#log_observer = ScrapyFileLogObserver(logfile, level=logging.DEBUG)
#log_observer.start()

# Spider for crawling Adidas website for shoes
class ForumsSpider(CrawlSpider):
    name = "lymphoma_forumslymphoma_spider"
    allowed_domains = ["lymphoma.com"]
    start_urls = [
        "http://forums.lymphoma.com",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                    restrict_xpaths='//td[@class="alt1Active"]/a',
                    canonicalize=True,
                ), callback='parsePostsList'),
            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                    restrict_xpaths='//div[@class="pagenav"]/a[@class="smallfont"]',
                    canonicalize=True,
                ), follow=True),
        )
    
    def getDate(self,date_str):
        # date_str="Fri Feb 12, 2010 1:54 pm"
        try:
            date = dateparser.parse(date_str)
            epoch = int(date.strftime('%s'))
            create_date = time.strftime("%Y-%m-%d'T'%H:%M%S%z",  time.gmtime(epoch))
            return create_date
        except Exception:
            #logging.error(">>>>>"+date_str)
            return date_str

    # https://github.com/scrapy/dirbot/blob/master/dirbot/spiders/dmoz.py
    # https://github.com/scrapy/dirbot/blob/master/dirbot/pipelines.py
    def parsePostsList(self,response):
        sel = Selector(response)
        posts = sel.css(".vt_post_holder")
        items = []
        topic = response.css('h1.caps').xpath('text()').extract()[0]
        url = response.url
        condition="lymphoma"
        for post in posts:
            item = PostItemsList()
            item['author'] = post.css('.vt_asked_by_user').xpath("./a").xpath("text()").extract()[0]
            item['author_link']=post.css('.vt_asked_by_user').xpath("./a").xpath("@href").extract()[0]
            item['condition']=condition
            create_date= post.css('.vt_first_timestamp').xpath('text()').extract().extend(response.css('.vt_reply_timestamp').xpath('text()').extract())
            item['create_date']= self.getDate(create_date)
            item['domain'] = "".join(self.allowed_domains)
            item['post'] = self.cleanText(" ".join(post.css('.vt_post_body').xpath('text()').extract()))
            # item['tag']='Lymphoma'
            item['topic'] = topic
            item['url']=url
            logging.info(item.__str__)
            items.append(item)
        return items
