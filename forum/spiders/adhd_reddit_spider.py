# -*- coding: utf-8 -*-
import scrapy
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
    name = "adhd_reddit_spider"
    allowed_domains = ["reddit.com"]
    start_urls = [
        "https://www.reddit.com/r/ADHD",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                    restrict_xpaths='//a[@class="title may-blank "]',
                    canonicalize=True,
                ), callback='parsePostsList'),
            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                    restrict_xpaths='//span[@class="nextprev"]',
                    canonicalize=True,
                    deny=(r'user_profile_*\.html',)
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
            
    def cleanText(self,text):
        soup = BeautifulSoup(text,'html.parser')
        text = soup.get_text();
        text = re.sub("( +|\n|\r|\t|\0|\x0b|\xa0|\xbb|\xab)+",' ',text).strip()
        return text 

    # https://github.com/scrapy/dirbot/blob/master/dirbot/spiders/dmoz.py
    # https://github.com/scrapy/dirbot/blob/master/dirbot/pipelines.py
    def parsePostsList(self,response):
        sel = Selector(response)
        posts = sel.xpath('//div[@class="entry unvoted"]')
        items = []
        topic = ''.join(response.xpath('//a[@class="title may-blank"]/text()').extract())
        url = response.url
        condition="adhd"
        
        for post in posts:
            item = PostItemsList()
            item['author'] = ''.join(post.xpath('.//a[contains(@class, "author may-blank")]/text()').extract())
            item['author_link'] = ''.join(post.xpath('.//a[contains(@class, "author may-blank")]/@href').extract())
            item['condition']=condition
            item['create_date']= self.getDate(''.join(post.xpath('.//time/@title').extract()))
            message = ''.join(post.xpath('.//div[@class="usertext-body may-blank-within md-container "]//text()').extract())
            item['post'] = self.cleanText(message)
            # item['tag']='adhd'
            item['topic'] = topic
            item['url']=url
            items.append(item)
        return items
