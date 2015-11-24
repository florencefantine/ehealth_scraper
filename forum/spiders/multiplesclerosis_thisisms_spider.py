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
# from helpers import cleanText


class ForumsSpider(CrawlSpider):
    name = "multiplesclerosis_thisisms_spider"
    allowed_domains = ["thisisms.com"]
    start_urls = [
        "http://www.thisisms.com/forum/general-discussion-f1/",
    ]

    rules = (
        Rule(LinkExtractor(
            restrict_xpaths='//a[@class="topictitle"]',
        ), callback="parsePostsList", follow=True),

        Rule(LinkExtractor(
            allow=(r"/page\d+\.html$"),
        ), follow=True),

        Rule(LinkExtractor(
            allow=(r"/topic\d+-\d+\.html$"),
        ), callback="parsePostsList", follow=True),
    )

    def cleanText(self,text,printableOnly=True):
        soup = BeautifulSoup(text,'html.parser')
        text = soup.get_text();
        text = re.sub("(-+| +|\n|\r|\t|\0|\x0b|\xa0|\xbb|\xab)+",' ',text).strip()
        if(printableOnly):
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

    def parsePostsList(self, response):
        items = []
        posts = response.xpath(
            '//div[@class="post bg2"] | //div[@class="post bg1"]')

        url = response.url
        subject = response.xpath('//div[@id="page-body"]/h2/a/text()')\
            .extract()[0]
        condition="multiple sclerosis"
        for post in posts:
            author = post.xpath(
                './/p[@class="author"]/strong/a/text()').extract()[0]

            author_link = post.xpath(
                './/p[@class="author"]/strong/a/@href').extract()[0]

            create_date = post.xpath(
                './/p[@class="author"]/text()').extract()[1]
            create_date = create_date.replace(u" \xbb", u"")

            message = " ".join(post.xpath(
                './/div[@class="content"]//text()').extract())
            message = self.cleanText(message)

            item = PostItemsList()
            item['author'] = author
            item['author_link'] = author_link
            item['condition'] = condition
            item['create_date'] = self.getDate(create_date)
            item['domain'] = "".join(self.allowed_domains)
            item['post'] = message
            # item['tag'] = 'epilepsy'
            item['topic'] = subject
            item['url'] = url

            items.append(item)
        return items
