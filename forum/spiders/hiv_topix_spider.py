# -*- coding: utf-8 -*-
import scrapy
import hashlib
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
    name = "hiv_topix_spider"
    allowed_domains = ["topix.com"]
    start_urls = [
        "http://www.topix.com/forum/health/hiv-aids",
    ]

    rules = (
            Rule(LinkExtractor(
                restrict_xpaths='//table[contains(@class,"thread_table")]/tr',
                canonicalize=True,
                deny='http://www.topix.com/member/profile/',
                ), callback='parsePost', follow=True),
            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                restrict_xpaths="//a[contains(@class, 'x-thread-pagination')]",
                deny='http://www.topix.com/member/profile/',
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
            
    def parsePost(self,response):
        logging.info(response)
        sel = Selector(response)
        posts = sel.css(".post_table").xpath('./tr')
        items = []
        if len(posts)==0:
            return items
        topic = response.xpath('//div[contains(@class,"str-forum-header")]/h1/text()').extract()[0]
        url = response.url
        condition = "hiv"
        for post in posts:
            item = PostItemsList()
            if len(post.css('.regsn'))>0:
                item['author'] = post.css('.regsn').xpath('./a/text()').extract()[0]
                item['author_link']=response.urljoin(post.css('.regsn').xpath('./a/@href').extract()[0])
            elif len(post.css('.x-author'))>0:
                item['author'] = post.css('.x-author').xpath("text()").extract()[0]
                item['author_link']=''
            else:
                continue
            item['condition'] = condition
            create_date =re.sub(r'^#\d+','',self.parseText(str=post.css('.x-comment-info').extract()[0]))
            item['create_date']= self.getDate(create_date)
            item['post']=self.parseText(" ".join(post.css('.x-post-content').extract()))
            item['topic'] = topic
            item['url']=url
            items.append(item)
        return items

    def parseText(self, str):
        soup = BeautifulSoup(str, 'html.parser')
        return re.sub(" +|\n|\r|\t|\0|\x0b|\xa0",' ',soup.get_text()).strip()
