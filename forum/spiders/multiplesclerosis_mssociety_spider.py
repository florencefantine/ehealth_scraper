# -*- coding: utf-8 -*-
import scrapy
from scrapy.contrib.spiders import Spider, Request, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.selector import Selector
from forum.items import PostItemsList
import re
import logging
from bs4 import BeautifulSoup
from selenium import webdriver
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
class ForumsSpider(Spider):
    name = "multiplesclerosis_mssociety_spider"
    allowed_domains = ["mssociety.org.uk"]
#    start_urls = [
#        "http://www.healingwell.com/community/default.aspx?f=23&m=1001057",
#    ]
    start_urls = [
        "https://community.mssociety.org.uk/forums/everyday-living/",
        "https://community.mssociety.org.uk/forums/new-diagnosis-and-diagnosis/",
        "https://community.mssociety.org.uk/forums/caring-someone-ms/",
        "https://community.mssociety.org.uk/forums/primary-progressive-ms/",
        "https://community.mssociety.org.uk/forums/asian-ms-support-group/"
    ]

    driver = webdriver.PhantomJS()

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
            
    def parse(self, response):
        self.driver.get(response.url)
        el = Selector(text=self.driver.page_source).xpath('//*[@id="forum-topic-list"]/table[2]/tbody/tr/td[2]/a/@href')
        requestList=[]
        for r in el.extract():
            requestList.append(Request(response.urljoin(r), callback=self.parsePost))

        el = Selector(text=self.driver.page_source).xpath('//ul[contains(@class, "pager")]/li/a/@href')
        for r in el.extract():
            # logging.info("url: "+r)
            requestList.append(Request(response.urljoin(r)))

        if len(requestList)>0:
            return requestList
        self.driver.close()


    # https://github.com/scrapy/dirbot/blob/master/dirbot/spiders/dmoz.py
    # https://github.com/scrapy/dirbot/blob/master/dirbot/pipelines.py
    def parsePost(self,response):
        items = []
        self.driver.get(response.url)
        logging.info(">>> "+response.body)
        sel = Selector(text=self.driver.page_source)
        comment = sel.xpath('//*[@id="forum-comments"]')
        topic = sel.xpath('//div[contains(@class, "forum-post")]')[0].xpath('.//div[contains(@class, "forum-post-title")]/text()').extract()[0].strip()
        url = response.url
        condition = "multiple sclerosis"
        post = sel.xpath('//div[contains(@class, "forum-post")]')[0]
        item = PostItemsList()
        if len(post.css('.author-name').xpath('./a/text()'))>0:
            item['author'] = post.css('.author-name').xpath('./a/text()').extract()[0]
            item['author_link']=response.urljoin(post.css('.author-name').xpath('./a/@href').extract()[0])
        else:
            item['author']=''
            item['author_link']=''
        item['condition'] = condition
        create_date= self.parseText(str=post.xpath('./div[1]/div').extract()[0])
        item['create_date']= self.getDate(create_date)
        post_msg= self.parseText(str=post.css('.forum-post-content').extract()[0])
        item['post']=post_msg
        # item['tag']='Multiple Sclerosis'
        item['topic'] = topic
        item['url']=url
        # logging.info(post_msg)
        items.append(item)

        if len(comment)==0:
            return items
        else:
            posts=comment.xpath('./div')
        for post in posts:
            item = PostItemsList()
            if len(post.css('.author-name'))>0:
                if len(post.css('.author-name').xpath('./a/text()'))>0:
                    item['author'] = post.css('.author-name').xpath('./a/text()').extract()[0]
                    item['author_link']=response.urljoin(post.css('.author-name').xpath('./a/@href').extract()[0])
                else:
                    item['author']=''
                    item['author_link']=''
            else:
                continue
            item['condition'] = condition
            create_date= self.parseText(str=post.xpath('./div[1]/div').extract()[0])
            item['create_date']= self.getDate(create_date)
            post_msg= self.parseText(str=post.css('.forum-post-content').extract()[0])
            item['post']=post_msg
            # item['tag']='Multiple Sclerosis'
            item['topic'] = topic
            item['url']=url
            # logging.info(post_msg)
            items.append(item)
        return items

    def parseText(self, str):
        soup = BeautifulSoup(str, 'html.parser')
        return re.sub(" +|\n|\r|\t|\0|\x0b|\xa0",' ',soup.get_text()).strip()
