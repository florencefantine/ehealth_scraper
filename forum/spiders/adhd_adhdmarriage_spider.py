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
    name = "adhd_adhdmarriage_spider"
    allowed_domains = ["adhdmarriage.com"]
    start_urls = [
        "http://www.adhdmarriage.com/forum",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                    restrict_xpaths='//td[@class="title"]',
                    canonicalize=True,
                ), callback='parsePostsList'),
            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                    restrict_xpaths='//tr[contains(@id,"forum-list")]',
                    canonicalize=True,
                    deny=(r'user_profile_*\.html',)
                ), follow=True),
            Rule(LinkExtractor(
                    restrict_xpaths='//li[contains(@class,"pager-item")]',
                    canonicalize=True,
                    deny=(r'user_profile_*\.html',)
                ), follow=True),


        )

    def cleanText(self,text,printableOnly=True):
        soup = BeautifulSoup(text,'html.parser')
        text = soup.get_text();
        text = re.sub("( +|\n|\r|\t|\0|\x0b|\xa0|\xbb|\xab)+",' ',text).strip()
        if printableOnly:
            return filter(lambda x: x in string.printable, text)
        return text

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
            
    # http://www.adhdmarriage.com/content/have-any-non-adhd-partners-been-able-find-happiness-adhd-partner
    def parsePostsList(self,response):
        sel = Selector(response)
        #posts = sel.css(".vt_post_holder")
        posts = sel.xpath('//article[contains(@class,"comment")]')
        items = []
        topic = ''.join(sel.xpath('//h1[@id="page-title"]/text()').extract()).strip()
        url = response.url
        condition="adhd"
            
        item = PostItemsList()
        item['author'] = sel.xpath('//header[@class="node-header"]//span[@class="username"]/text()').extract_first()
        item['author_link'] = '' 
        item['condition'] = condition
        #create_date = ''.join(sel.xpath('//span[@class="post-meta"]/text()').extract()).replace("Posted by","").replace("to","")
        create_date = sel.xpath('//header[@class="node-header"]//time/text()').extract()[0]
        item['create_date']= self.getDate(create_date)
        item['domain'] = "".join(self.allowed_domains)
        message = ''.join(sel.xpath('//header[@class="node-header"]//div[@class="field-items"]//text()').extract())
        item['post'] = self.cleanText(message)
        item['tag']=''
        item['topic'] = topic
        item['url']=url
        logging.info(item.__str__)
        items.append(item)

        for post in posts:
            item = PostItemsList()
            item['author'] = post.xpath('.//span[@class="username"]/text()').extract()[0]
            item['author_link'] = ''
            item['condition'] = condition
            create_date = post.xpath('.//span[@class="date-time"]/text()').extract()[0]
            item['create_date']= self.getDate(create_date)
            item['domain'] = "".join(self.allowed_domains)
            message = ''.join(post.xpath('.//div[@class="comment-content"]//text()').extract())
            item['post'] = self.cleanText(message)
            # item['tag']='adhd'
            item['topic'] = topic
            item['url']=url
            items.append(item)
        return items
