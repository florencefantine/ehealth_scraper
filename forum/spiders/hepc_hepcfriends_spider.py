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
    name = "hepc_hepcfriends_spider"
    allowed_domains = ["hepcfriends.activeboard.com"]
    start_urls = [
        "http://hepcfriends.activeboard.com/f388110/on-treatment/",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                    restrict_xpaths='//a[@class="topictitle"]',
                ), callback='parsePostsList'),
            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                    restrict_xpaths='//a[@title="Next"]'
                ), follow=True),
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

    # https://github.com/scrapy/dirbot/blob/master/dirbot/spiders/dmoz.py
    # https://github.com/scrapy/dirbot/blob/master/dirbot/pipelines.py
    def parsePostsList(self,response):
        sel = Selector(response)
        posts = sel.xpath('//table[@id="abPreviewTbl"]//tr[contains(@class, "tr")]')
        items = []
        topic = response.xpath('//div[@class="breadcrumb-widget widget gen"]/span[@class="nolinks"]/text()').extract_first()
        url = response.url
        condition="hepatitis c"
        
        for post in posts:
            item = PostItemsList()
            item['author'] = post.xpath('.//td[contains(@class, "td-first")]/div[@class="comment-meta"]/a/text()').extract_first()
            if item['author']:
                item['author_link'] = post.xpath('.//td[contains(@class, "td-first")]/div[@class="comment-meta"]/a/@href').extract_first()
                item['condition'] = condition
                create_date = post.xpath('.//td[contains(@class, "td-first")]//time/text()').extract_first()
                item['create_date'] = self.getDate(create_date)
                item['domain'] = "".join(self.allowed_domains)
                item['post'] = self.cleanText(" ".join(post.xpath('.//div[@class="comment-body postbody"]/p/text()').extract()))
                # item['tag']=''
                item['topic'] = topic
                item['url']=url
                items.append(item)
        return items
