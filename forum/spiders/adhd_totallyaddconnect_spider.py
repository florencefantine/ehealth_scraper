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
    name = "adhd_totallyaddconnect_spider"
    allowed_domains = ["totallyaddconnect.com"]
    start_urls = [
        "http://www.totallyaddconnect.com/forums",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                    restrict_xpaths='//td[@class="bbp-topic-title"]',
                    canonicalize=False,
                ), callback='parsePostsList'),
            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                    restrict_xpaths='//td[@class="bbp-forum-info"]',
                    canonicalize=False,
                    deny=(r'user_profile_*\.html',)
                ), follow=True),
            Rule(LinkExtractor(
                    restrict_xpaths='//td[@class="bbp-forum-title"]',
                    canonicalize=False,
                    deny=(r'user_profile_*\.html',)
                ), follow=True),
            Rule(LinkExtractor(
                    restrict_xpaths='//a[@class="page-numbers"]',
                    canonicalize=False,
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
            
    def cleanText(self,text,printableOnly=True):
        soup = BeautifulSoup(text,'html.parser')
        text = soup.get_text();
        text = re.sub("( +|\n|\r|\t|\0|\x0b|\xa0|\xbb|\xab)+",' ',text).strip()
        if(printableOnly):
            return filter(lambda x: x in string.printable, text)
        return text 

    def getDate(self,date_str):
        date_strs = date_str.split("#")
        return date_strs[0]

    # https://github.com/scrapy/dirbot/blob/master/dirbot/spiders/dmoz.py
    # https://github.com/scrapy/dirbot/blob/master/dirbot/pipelines.py
    def parsePostsList(self,response):
        sel = Selector(response)
        #posts = sel.css(".vt_post_holder")
        posts = sel.xpath('//table[@class="bbp-replies"]')
        items = []
        topic = ''.join(sel.xpath('//h1[@class="entry-title"]/text()').extract()).strip()
        url = response.url
        condition="adhd"
            
        item = PostItemsList()
        item['author'] = sel.xpath('//table[@class="bbp-topic"]//a[@class="bbp-author-name"]/text()').extract_first()
        item['author_link'] = sel.xpath('//table[@class="bbp-topic"]//a[@class="bbp-author-name"]/@href').extract_first()
        item['condition'] = condition
        create_date = ''.join(sel.xpath('//table[@class="bbp-topic"]//tr[@class="bbp-topic-header"]//text()').extract()).strip()
        item['create_date']= self.getDate(self.cleanText(create_date).replace("at",""))
        
        message = ''.join(sel.xpath('//td[@class="bbp-topic-content"]//text()').extract())
        item['post'] = self.cleanText(message).replace("[Report This Post]","")
        # item['tag']='adhd'
        item['topic'] = topic
        item['url']=url
        logging.info(item.__str__)
        items.append(item)

        for post in posts:
            item = PostItemsList()
            item['author'] = post.xpath('.//a[@class="bbp-author-name"]/text()').extract_first()
            item['author_link'] = post.xpath('.//a[@class="bbp-author-name"]/@href').extract_first()
            item['condition'] = condition
            create_date = ''.join(post.xpath('.//tr[@class="bbp-reply-header"]//text()').extract()).strip()
            item['create_date']= self.getDate(self.getDate(self.cleanText(create_date).replace("at","")).strip())
            
            message = ''.join(post.xpath('.//td[@class="bbp-reply-content"]//text()').extract())
            item['post'] = self.cleanText(message).replace("[Report This Post]","").strip()
            # item['tag']=''
            item['topic'] = topic
            item['url']=url
            logging.info(item.__str__)
            items.append(item)
        return items
