# -*- coding: utf-8 -*-
import scrapy
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.selector import Selector
from forum.items import PostItemsList
import re
import logging
from bs4 import BeautifulSoup
import string
import dateparser
import time
# import lxml.html
# from lxml.etree import ParserError
# from lxml.cssselect import CSSSelector

## LOGGING to file
#import logging
#from scrapy.log import ScrapyFileLogObserver

#logfile = open('testlog.log', 'w')
#log_observer = ScrapyFileLogObserver(logfile, level=logging.DEBUG)
#log_observer.start()

# Spider for crawling Adidas website for shoes
class ForumsSpider(CrawlSpider):
    name = "carcinoidcancer_cancerforums_spider"
    allowed_domains = ["cancerforums.net"]
#    start_urls = [
#        "http://www.healingwell.com/community/default.aspx?f=23&m=1001057",
#    ]
    start_urls = [
        "http://www.cancerforums.net/forums/22-Other-Cancers-Forum",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                restrict_xpaths='//h3[contains(@class, "threadtitle")]',
                canonicalize=True,
                ), callback='parsePost', follow=True),

            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                restrict_xpaths='//div[contains(@class, "threadpagenav")]',
                canonicalize=True,
                allow='http://www.cancerforums.net/forums/',
            ), follow=True),

            Rule(LinkExtractor(
                restrict_xpaths='//*[@id="pagination_bottom"]',
                canonicalize=True,
                allow='http://www.cancerforums.net/threads/',
            ), callback='parsePost', follow=True),
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
    def parsePost(self,response):
        logging.info(response)
        sel = Selector(response)
        posts = sel.xpath('//*[@id="posts"]/li')
        items = []
        topic = sel.css('.threadtitle').xpath('./a/text()').extract()[0]
        condition="carcinoid cancer"
        url = response.url
        for post in posts:
            item = PostItemsList()
            item['author'] = post.xpath('.//a[contains(@class, "username")]/strong/text()').extract()[0].strip()
            item['author_link']=response.urljoin(post.xpath('.//a[contains(@class, "username")]/@href').extract()[0])
            date = post.css('.postdate').extract()[0]
            soup = BeautifulSoup(date, 'html.parser')
            date=re.sub(" +|\n|\r|\t|\0|\x0b|\xa0",' ',soup.get_text()).strip()
            item['condition']=condition
            item['create_date']= self.getDate(date)
            # soup = BeautifulSoup(post_msg, 'html.parser')
            # post_msg = re.sub(" +|\n|\r|\t|\0|\x0b|\xa0",' ',soup.get_text()).strip()
            item['post']=self.cleanText(post.css('.postcontent').extract()[0])
            # item['tag']=''
            item['topic'] = topic
            item['url']=url
            items.append(item)
        return items
