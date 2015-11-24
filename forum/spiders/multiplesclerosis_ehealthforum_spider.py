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
    name = "multiplesclerosis_ehealthforum_spider"
    allowed_domains = ["ehealthforum.com"]
    start_urls = [
        "http://ehealthforum.com/health/multiple_sclerosis.html",
    ]

    rules = (
            Rule(LinkExtractor(
                restrict_xpaths='//*/a[@class="topictitle "]',
                canonicalize=True,
                allow='http://ehealthforum.com/health/.*\.html',
                ), callback='parsePost', follow=True),
            # Rule to follow arrow to next grid
            Rule(LinkExtractor(
                restrict_xpaths='//*/a[contains(text(),">>")]',
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
        posts = sel.xpath('//*/div[@class="vt_post_holder"]')
        items = []
        if not posts: return items
        topic = self.cleanText(response.xpath('//*[@id="page_h1"]').extract()[0].encode('ascii'))
        url = response.url
        condition = "multiple sclerosis"
        for post in posts:
            post_xp = post.xpath('./div[3]/div/div/div[1]')
            if not post_xp: continue
            post_msg = self.parseText(str=post_xp.extract()[0])

            item = PostItemsList()
            item['author'] = self.cleanText(post.xpath('./div[2]/div/span').extract()[0].encode('ascii'))
            item['author_link'] = post.xpath('./div[2]/div/span/a/@href').extract()[0]
            create_date_xp = post.xpath('./div[2]/div[3]/span')
            item['condition'] = condition
            if create_date_xp:
                create_date = self.parseText(str=create_date_xp.extract()[0]).replace('replied ','')
                item['create_date'] = self.getDate(create_date)
            else:
                create_date = self.parseText(str=post.xpath('./div/div[3]/div/div').extract()[0])
                item['create_date'] = self.getDate(create_date)
            item['post'] = post_msg
            item['tag'] = 'multiple-sclerosis'
            item['topic'] = topic
            item['url'] = url
            #logging.info(post_msg)
            items.append(item)

        return items

