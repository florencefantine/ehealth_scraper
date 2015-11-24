# -*- coding: utf-8 -*-
from scrapy.contrib.spiders import CrawlSpider, Rule
import hashlib
from scrapy.contrib.linkextractors import LinkExtractor
from forum.items import PostItemsList
import logging
from bs4 import BeautifulSoup
import re
import string
import dateparser
import time

# import lxml.html
# from lxml.etree import ParserError
# from lxml.cssselect import CSSSelector

# LOGGING to file
# import logging
# from scrapy.log import ScrapyFileLogObserver

# logfile = open('testlog.log', 'w')
# log_observer = ScrapyFileLogObserver(logfile, level=logging.DEBUG)
# log_observer.start()

# Spider for crawling Adidas website for shoes


class ForumsSpider(CrawlSpider):
    name = "adhd_ldonline_spider"
    allowed_domains = ["ldonline.org"]
    start_urls = [
        "http://www.ldonline.org/xarbb/?catid=769",
    ]

    rules = (
        Rule(
            LinkExtractor( restrict_xpaths='//span[@class="xar-title"]/a', canonicalize=True),
            follow=True),

        Rule(LinkExtractor(
            restrict_xpaths='//a[contains(@title, "Next 10 pages")]',canonicalize=True),
            follow=True),

        Rule(LinkExtractor(
            restrict_xpaths='//td[@class="xar-norm icon"]/a',canonicalize=True),
            callback="topic_parse", follow=True),
    )

    def cleanText(self,text):
        soup = BeautifulSoup(text,'html.parser')
        text = soup.get_text();
        text = re.sub("( +|\n|\r|\t|\0|\x0b|\xa0|\xbb|\xab)+",' ',text).strip()
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

    # http://www.ldonline.org/xarbb/topic/33120
    def topic_parse(self, response):
        items = []
        condition='adhd'
        subject = response.xpath(
            '//title/text()').extract()[0]
        subject = subject.split('|')[0]
        url = response.url
        posts = response.xpath('//table//tr')[1:-1:2]

        for post in posts:
            item = PostItemsList()
            author = post.xpath(
                './/td[@class="xar-norm author"]/*/a/text()').extract()[0]
            author_link = post.xpath(
                './/td[@class="xar-norm author"]/*/a/@href').extract()[0]
            create_date = re.sub(r'^:','',self.cleanText(post.xpath(
                './/span[@class="xar-sub"][contains(text(), "Posted")]/text()'
            ).extract()[0].replace("Posted","").replace("Posted:","").replace("at",",")))
            message = ''.join(post.xpath(
                './/div[2]/p//text()'
            ).extract())
            message = self.cleanText(message)

            item['author'] = author
            item['author_link'] = author_link
            item['condition'] = condition
            item['create_date'] = self.getDate(create_date)
            item['domain'] = "".join(self.allowed_domains)
            item['post'] = self.cleanText(message)
            # item['tag'] = ''
            item['topic'] = subject
            item['url'] = url

            items.append(item)
        return items
