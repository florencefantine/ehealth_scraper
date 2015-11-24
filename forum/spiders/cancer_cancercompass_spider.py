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

# Spider for crawling Adidas website for shoes
class ForumsSpider(CrawlSpider):
    name = "cancer_cancercompass_spider"
    allowed_domains = ["www.cancercompass.com"]
    start_urls = [
        "http://www.cancercompass.com/message-board/cancers/lung-cancer/1,0,119,3.htm",
        "http://www.cancercompass.com/message-board/cancers/lung-cancer/non-small-cell/1,0,119,3,54.htm",
        "http://www.cancercompass.com/message-board/cancers/prostate-cancer/1,0,119,2.htm",
        'http://www.cancercompass.com/message-board/cancers/lymphoma/1,0,119,57.htm',
        'http://www.cancercompass.com/message-board/cancers/lymphoma/non-hodgkins/1,0,119,57,58.htm',
        'http://www.cancercompass.com/message-board/cancers/breast-cancer/1,0,119,1.htm',
        "http://www.cancercompass.com/message-board/cancers/leukemia/leukemia-(cll)/1,0,119,7,50.htm",
        "http://www.cancercompass.com/message-board/cancers/renal-cell-cancer/1,0,119,131.htm?sortby=replies&dir=1"
    ]

    rules = (
            Rule(LinkExtractor(
                    restrict_xpaths='//a[@class="subLink"]',
                ), callback='parsePostsList'),
            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                    restrict_xpaths='//span[@id="MainContent_ContentPlaceHolder1_discussionList_dtpDis"]/a[last()]'
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
            
    def cleanText(self, str):
        soup = BeautifulSoup(str, 'html.parser')
        return re.sub(" +|\n|\r|\t|\0|\x0b|\xa0",' ',soup.get_text()).strip()

    def parsePostsList(self,response):
        sel = Selector(response)
        posts = sel.xpath('//div[@class="mbpost"]')
        items = []
        condition = "cancer"
        topic = response.xpath('//h1/text()').extract_first()
        url = response.url
        for post in posts:
            item = PostItemsList()
            item['author'] = post.xpath('.//div[@class="header"]/p/a/text()').extract_first()
            item['author_link'] = post.xpath('.//div[@class="header"]/p/a/@href').extract_first()
            item['condition'] = condition
            item['create_date'] = self.getDate(post.xpath('.//div[@class="header"]/p/text()').extract()[1].replace('on','').strip())
            item['post'] = self.cleanText(" ".join(post.xpath('.//div[@class="msgContent"]/p/text()').extract()))
            # item['tag']=''
            item['topic'] = topic
            item['url']=url
            logging.info(item.__str__)
            items.append(item)
        return items
