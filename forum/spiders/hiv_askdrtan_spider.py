# -*- coding: utf-8 -*-
import scrapy
import hashlib
from scrapy.contrib.spiders import CrawlSpider, Rule, Spider, Request
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
    name = "hiv_askdrtan_spider"
    allowed_domains = ["askdrtan.com"]
#    start_urls = [
#        "http://www.healingwell.com/community/default.aspx?f=23&m=1001057",
#    ]
    start_urls = [
        "http://www.askdrtan.com/forum/view",
    ]

    # rules = (
    #         # Rule to go to the single product pages and run the parsing function
    #         # Excludes links that end in _W.html or _M.html, because they point to
    #         # configuration pages that aren't scrapeable (and are mostly redundant anyway)
    #         Rule(LinkExtractor(
    #             restrict_xpaths='//*[@id="content"]/table/tbody/tr',
    #             canonicalize=True,
    #             ), callback='parsePost', follow=True),
    #
    #         Rule(LinkExtractor(
    #             restrict_xpaths='//ul[contains(@class, "pagination")]',
    #             canonicalize=True,
    #             ), follow=True),
    #     )

    # driver = webdriver.Chrome('G:\\tools\\chromedriver.exe')
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
        el = Selector(text=self.driver.page_source).xpath('//*[@id="content"]/table/tbody/tr/td[1]/a/@href')
        requestList=[]
        for r in el.extract():
            requestList.append(Request(response.urljoin(r), callback=self.parsePost))

        el = Selector(text=self.driver.page_source).xpath('//ul[contains(@class, "pagination")]/li/a/@href')
        for r in el.extract():
            requestList.append(Request(response.urljoin(r)))

        if len(requestList)>0:
            return requestList
        else:
            self.driver.find_element_by_xpath('//*[@id="content"]/div[1]/div[1]/a').click()
            self.driver.get(response.url)
            el = Selector(text=self.driver.page_source).xpath('//*[@id="content"]/table/tbody/tr/td[1]/a/@href')
            requestList=[]
            for r in el.extract():
                requestList.append(Request(response.urljoin(r), callback=self.parsePost))
            el = Selector(text=self.driver.page_source).xpath('//ul[contains(@class, "pagination")]/li/a/@href')
            for r in el.extract():
                requestList.append(Request(response.urljoin(r)))
            if len(requestList)>0:
                return requestList
        self.driver.close()


    def cleanText(self,text,printableOnly=True):
        soup = BeautifulSoup(text,'html.parser')
        text = soup.get_text();
        text = re.sub("(-+| +|\n|\r|\t|\0|\x0b|\xa0|\xbb|\xab)+",' ',text).strip()
        if(printableOnly):
            return filter(lambda x: x in string.printable, text)
        return text 

    # https://github.com/scrapy/dirbot/blob/master/dirbot/spiders/dmoz.py
    # https://github.com/scrapy/dirbot/blob/master/dirbot/pipelines.py
    def parsePost(self,response):
        logging.info(response)
        sel = Selector(response)
        items = []
        if len(sel.xpath('//*[@id="content"]/table/thead/tr/th[1]'))==0:
            return items
        topic = ''
        # item='hiv'
        condition = "hiv"
        url = response.url
        item = PostItemsList()
        item['author'] = self.cleanText(sel.xpath('//*[@id="content"]/table/thead/tr/th[1]/span/text()').extract()[0])
        item['author_link']=""
        date = sel.xpath('//*[@id="content"]/table/thead/tr/th[2]/span/text()').extract()[0]

        item['create_date']=date
        post_msg=sel.xpath('//*[@id="content"]/table/tbody/tr[1]/td/p').extract()[0]
        soup = BeautifulSoup(post_msg, 'html.parser')
        item['domain'] = "".join(self.allowed_domains)
        post_msg = re.sub(" +|\n|\r|\t|\0|\x0b|\xa0",' ',soup.get_text()).strip()
        item['post']=post_msg
        # item['tag']='hiv'
        item['topic'] = topic
        item['url']=url
        logging.info(post_msg)
        items.append(item)

        item = PostItemsList()
        item['author'] = self.cleanText(sel.xpath('//*[@id="content"]/table/tbody/tr[2]/td/div[1]').extract()[0])
        item['author_link']=""
        item['condition'] = condition
        item['create_date'] = self.getDate(date)
        post_msg = sel.xpath('//*[@id="content"]/table/tbody/tr[2]/td/p').extract()[0]
        soup = BeautifulSoup(post_msg, 'html.parser')
        post_msg = re.sub(" +|\n|\r|\t|\0|\x0b|\xa0",' ',soup.get_text()).strip()
        item['post']=post_msg
        # item['tag']='hiv'
        item['topic'] = topic
        item['url']=url
        logging.info(post_msg)
        items.append(item)
        return items
