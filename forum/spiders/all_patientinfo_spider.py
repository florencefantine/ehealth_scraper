# -*- coding: utf-8 -*-
import scrapy
from scrapy.contrib.spiders import Spider, Rule, Request
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

class ForumsSpider(Spider):
    name = "all_patientinfo_spider"
    allowed_domains = ["patient.info"]
    start_urls = [
        "http://patient.info/forums/discuss/browse/epilepsy-801",
        "http://patient.info/health/non-hodgkins-lymphoma-leaflet/discuss",
        "http://patient.info/forums/discuss/browse/rheumatoid-arthritis-1968",
        "http://patient.info/forums/discuss/browse/prostate-cancer-1816"
    ]

    driver = webdriver.PhantomJS()


    def getDate(self,date_str):
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
        logging.info("parse url: "+response.url)
        el = Selector(text=self.driver.page_source).xpath('//ul[contains(@class, "thread-list")]/li//h3[contains(@class, "title")]/a/@href')
        requestList=[]
        for r in el.extract():
            requestList.append(Request(response.urljoin(r), callback=self.parsePost))

        el = Selector(text=self.driver.page_source).xpath('//*[@id="group-discussions"]/form[1]/a')
        for r in el.extract():
            logging.info("url: "+r)
            requestList.append(Request(response.urljoin(r), callback=self.parsePost))

        if len(requestList)>0:
            return requestList
        self.driver.close()

    def parsePost(self,response):
        logging.info(response)
        self.driver.get(response.url)
        sel = Selector(text=self.driver.page_source)
        posts = sel.xpath('//ul[contains(@class, "replies")]/li')
        items = []
        topic = self.cleanText(sel.xpath('//*[@id="topic"]/article/h1/text()').extract()[0])
        url = response.url
        condition = topic
        post = sel.xpath('//*[@id="topic"]')
        item = PostItemsList()
        item['author'] = post.xpath('./div/a/p/strong[2]/text()').extract()[0].strip()
        item['author_link']=response.urljoin(post.xpath("./div/a/@href").extract()[0])
        item['condition'] = condition
        item['create_date']= self.cleanText(post.xpath('./article/span/time/@title').extract()[0])
        post_msg=self.cleanText(post.xpath('./article/div/p').extract()[0])
        item['post']=post_msg
        # item['tag']='rheumatoid arthritis'
        item['topic'] = topic
        item['url']=url
        
        items.append(item)

        for post in posts:
            item = PostItemsList()
            if len(post.css('.avatar')) == 0:
                continue
            item['author'] = post.xpath("./article/span[1]/a[1]/text()").extract()[0].strip()
            item['author_link']=response.urljoin(post.xpath("./article/span[1]/a[1]/@href").extract()[0])
            item['condition'] = condition
            item['create_date']= self.getDate(self.cleanText(post.xpath('./article/span[2]/time/@title').extract()[0]))
            post_msg=self.cleanText(post.xpath('./article/div[1]/p').extract()[0])
            item['post']=post_msg
            item['topic'] = topic
            item['url']=url
            logging.info(post_msg)
            items.append(item)
        return items

    def cleanText(self,text, printableOnly =True):
        soup = BeautifulSoup(text,'html.parser')
        text = soup.get_text();
        text = re.sub("( +|\n|\r|\t|\0|\x0b|\xa0|\xbb|\xab)+",' ',text).strip()
        if printableOnly:
            return filter(lambda x: x in string.printable, text)
        return text




# import scrapy
# from scrapy.contrib.spiders import CrawlSpider, Rule
# from scrapy.contrib.linkextractors import LinkExtractor
# from scrapy.selector import Selector
# from forum.items import PostItemsList
# import re
# from bs4 import BeautifulSoup
# import logging
# import string
# import dateparser
# import time

# class ForumsSpider(CrawlSpider):
#     name = "all_patientinfo_spider"
#     allowed_domains = ["patient.info"]
#     start_urls = [
#         "http://patient.info/forums/discuss/browse/epilepsy-801",
#         "http://patient.info/health/non-hodgkins-lymphoma-leaflet/discuss",
#     ]

#     rules = (
#             Rule(LinkExtractor(
#                     restrict_xpaths='//ul[@class="thread-list"]/li//h3/a',
#                     canonicalize=True,
#                 ), callback='parsePostsList'),
#             # Rule to follow arrow to next product grid
#             Rule(LinkExtractor(
#                     restrict_xpaths='//a[@class="reply-ctrl-wrap reply-ctrl-last"][last()]',
#                     canonicalize=True,
#                 ), follow=True),
#         )

#     def getDate(self,date_str):
#         # date_str="Fri Feb 12, 2010 1:54 pm"
#         try:
#             date = dateparser.parse(date_str)
#             epoch = int(date.strftime('%s'))
#             create_date = time.strftime("%Y-%m-%d'T'%H:%M%S%z",  time.gmtime(epoch))
#             return create_date
#         except Exception:
#             #logging.error(">>>>>"+date_str)
#             return date_str
            
#     def parsePostsList(self,response):
#         sel = Selector(response)
#         posts = sel.xpath('//div[@id="topic-replies"]//article[contains(@class,"post")]')
#         items = []
#         topic = response.xpath('//h1[@class="title"]/text()').extract_first()
#         url = response.url
        
#         item = PostItemsList()
#         item['author'] = response.xpath('//div[@id="topic"]/div[@class="avatar"]/a/p/strong[1]/text()').extract_first()
#         item['author_link'] = response.xpath('//div[@id="topic"]/div[@class="avatar"]/a/@href').extract_first()
#         item['condition']=topic
#         item['create_date'] = self.getDate(response.xpath('//div[@id="topic"]//article//time/@datetime').extract_first().strip())
#         item['post'] = re.sub('\s+',' '," ".join(response.xpath('//div[@id="topic"]//div[@class="post-content break-word"]/p/text()').extract()).replace("\t","").replace("\n","").replace("\r",""))
#         item['topic'] = topic
#         item['url']=url
#         items.append(item)
        
#         for post in posts:
#             item = PostItemsList()
#             item['author'] = post.xpath('./span[@class="post-username"]/a/text()').extract_first()
#             item['author_link'] = post.xpath('./span[@class="post-username"]/a/@href').extract_first()
#             item['condition']=topic
#             item['create_date'] = self.getDate(post.xpath('.//time/@datetime').extract_first())
#             item['post'] = re.sub('\s+',' '," ".join(post.xpath('./div[@class="post-content break-word"]/p/text()').extract()).replace("\t","").replace("\n","").replace("\r",""))
#             item['topic'] = topic
#             item['url']=url
#             items.append(item)
#         return items
