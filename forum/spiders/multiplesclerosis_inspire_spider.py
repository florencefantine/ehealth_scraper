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

## LOGGING to file
#import logging
#from scrapy.log import ScrapyFileLogObserver

#logfile = open('testlog.log', 'w')
#log_observer = ScrapyFileLogObserver(logfile, level=logging.DEBUG)
#log_observer.start()


# Spider for crawling multiple-sclerosis board
class ForumsSpider(CrawlSpider):
    name = "multiplesclerosis_inspire_spider"
    allowed_domains = ["inspire.com"]
    start_urls = [
        "https://www.inspire.com/search/?query=multiple+sclerosis",
    ]

    rules = (
            Rule(LinkExtractor(
                restrict_xpaths='//*[@id="search-results"]/h3',
                canonicalize=True,
                allow='http.://(www\.)?inspire.com/groups/.*',
                ), callback='parsePost', follow=False),
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
        text = re.sub("(-+| +|\n|\r|\t|\0|\x0b|\xa0|\xbb|\xab)+",' ',text).strip()
        if(printableOnly):
            return filter(lambda x: x in string.printable, text)
        return text 

    def parseText(self, str):
        soup = BeautifulSoup(str, 'html.parser')
        return re.sub(" +|\n|\r|\t|\0|\x0b|\xa0",' ',soup.get_text()).strip()

    def parsePost(self,response):
        #logging.info(response)
        sel = Selector(response)
        items = []
        topic = self.cleanText(response.xpath('//*[@class="post-title"]').extract()[0].encode('ascii'))
        url = response.url
        condition = "multiple sclerosis"

        #start message
        item = PostItemsList()
        post_info = sel.xpath('//*/div[@class="post-info"]')
        item['author'] = self.cleanText(post_info.xpath('//*/li[@class="by"]/a').extract()[0])
        item['author_link'] = post_info.xpath('//*/li[@class="by"]/a/@href').extract()[0]
        item['condition'] = condition
        create_date = self.cleanText(post_info.xpath('//*/ul/li[@class="by"]').extract()[0]).split(u'\xb7')[1].strip()
        item['create_date'] = self.getDate(create_date)
        item['post'] = post_info.xpath('//*[@class="post-body"]').extract()[0]
        # item['tag'] = 'multiple-sclerosis'
        item['topic'] = topic
        item['url'] = url
        items.append(item)

        posts = sel.xpath('//*/div[@class="comments-box"]')
        if not posts: return items
        for post in posts:
            post_xp = post.xpath('./p')
            if not post_xp: continue
            post_msg = self.parseText(str=post_xp.extract()[0])

            item = PostItemsList()
            item['author'] = self.cleanText(post.xpath('./div/ul/li[1]/a').extract()[0])
            item['author_link'] = post.xpath('./div/ul/li[1]/a/@href').extract()[0]
            item['condition'] = condition
            create_date = self.cleanText(post.xpath('./div/ul/li[3]').extract()[0])
            item['create_date'] = self.getDate(create_date)
            item['post'] = post_msg
            # item['tag'] = 'multiple-sclerosis'
            item['topic'] = topic
            item['url'] = url
            #logging.info(post_msg)
            items.append(item)

        return items

