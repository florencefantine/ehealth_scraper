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
    name = "multiplesclerosis_msworld_spider"
    allowed_domains = ["msworld.org"]
    start_urls = [
        "http://www.msworld.org/forum/",
    ]


    rules = (
        Rule(LinkExtractor(
            restrict_xpaths='//h2[@class="forumtitle"]',
        ), callback="replace_link", follow=True),

        Rule(LinkExtractor(
            allow=(r"forumdisplay\.php\?.+/page\d+")
        ), callback="replace_link", follow=True),

        Rule(LinkExtractor(
            allow=(r"showthread.php")
        ), callback="parsePostsList", follow=True),
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


    def replace_link(self, response):
        # little hack for remove request string from url
        url = response.url.split("=&")[0]
        yield scrapy.Request(url, self.parsePostsList)

    def parsePostsList(self, response):
        items = []
        url = response.url
        condition="multiple sclerosis"
        subject = self.cleanText(" ".join(response.xpath(
            '//li[@class="navbit lastnavbit"]/span/text()').extract()))
        posts = response.xpath(
            '//li[@class="postbit postbitim postcontainer old"]')
        for post in posts:
            item = PostItemsList()
            author = post.xpath(
                './/a[contains(@class, "username")]/strong/text()')\
                .extract()[0]
            author_link = post.xpath(
                './/a[contains(@class, "username")]/@href').extract()[0]
            author_link = response.urljoin(author_link)
            create_date = " ".join(post.xpath(
                './/span[@class="date"]//text()').extract())
            message = " ".join(post.xpath(
                './/div[contains(@id, "post_message_")]//text()').extract())
            message = self.cleanText(message)

            item['author'] = author
            item['author_link'] = author_link
            item['condition'] = condition
            item['create_date'] = self.getDate(self.cleanText(create_date))
            item['post'] = message
            # item['tag'] = 'epilepsy'
            item['topic'] = subject
            item['url'] = url

            items.append(item)
        return items
