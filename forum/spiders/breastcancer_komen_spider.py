# -*- coding: utf-8 -*-
import scrapy
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from forum.items import PostItemsList
import re
from bs4 import BeautifulSoup
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
    name = "breastcancer_komen_spider"
    allowed_domains = ["komen.org"]
    start_urls = [
        "https://apps.komen.org/Forums/",
    ]

    def cleanText(self,text):
        soup = BeautifulSoup(text,'html.parser')
        text = soup.get_text();
        text = re.sub("( +|\n|\r|\t|\0|\x0b|\xa0|\xbb|\xab)+",' ',text).strip()
        return text 
    
    def parse(self, response):
        for url in response.xpath('//a[@class="forumlink"]/@href').extract():
            url = response.urljoin(url)
            yield scrapy.Request(url,
                callback=self.forum_parse,
                cookies={"KomenForumApptimefilter": "0"}
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
            
    def forum_parse(self, response):
        # print("=" * 50)
        # print(response.url)
        for topic in response.xpath(
                '//a[contains(@id, "msgSubjectLink")]/@href').extract():
            topic = response.urljoin(topic)
            yield scrapy.Request(topic, self.topic_parse,
                                 cookies={"KomenForumApptimefilter": "0"})
        next_page = response.xpath(
            '//a[@class="paging"][contains(text(), ">")]/@href').extract()
        if len(next_page) > 0:
            yield scrapy.Request(response.urljoin(next_page[0]),
                                 callback=self.forum_parse,
                                 cookies={"KomenForumApptimefilter": "0"}
                                 )

    def topic_parse(self, response):
        items = []
        condition="breast cancer"
        subject = response.xpath(
            '//div[@class="for_title"]/text()').extract()[0]
        subject = self.cleanText(subject)
        next_page = response.xpath(
            '//a[@class="paging"][last()]/@href').extract()
        posts = response.xpath('//table[contains(@id, "msg_tbl")]')
        url = response.url
        for post in posts:
            item = PostItemsList()
            author = post.xpath(
             './/a[@class="titlehead"]/text()'
                ).extract()[0]
            author_link = post.xpath(
             './/a[@class="titlehead"]/@href'
                ).extract()[0]
            author_link = response.urljoin(author_link)

            message = "".join(post.xpath(
             './/div[@class="msg"]//text()'
                ).extract())
            message = self.cleanText(message)

            create_date = post.xpath(
             './/span[contains(@id, "date")]/text()'
                ).extract()[0].strip()

            item['author'] = author
            item['author_link'] = author_link
            item['condition'] = condition
            item['create_date'] = self.getDate(re.sub(r'^-\s+','',self.cleanText(create_date)))
            item['post'] = message
            # item['tag'] = ''
            item['topic'] = subject
            item['url'] = url
            yield item
            # items.append(item)
        # yield {"items": items}


        if len(next_page) > 0:
            next_page = response.urljoin(next_page[0])
            print("!"*100)
            yield scrapy.Request(url,
                                 callback=self.topic_parse,
                                 cookies={"KomenForumApptimefilter": "0"}
                                 )
