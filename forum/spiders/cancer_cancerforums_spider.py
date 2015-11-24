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
    name = "cancer_cancerforums_spider"
    allowed_domains = ["www.cancerforums.net"]
    start_urls = [
        "http://www.cancerforums.net/forums/13-Lung-Cancer-Forum",
        "http://www.cancerforums.net/forums/14-Prostate-Cancer-Forum"
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                    restrict_xpaths='//h3/a[@class="title"]',
                ), callback='parsePostsList'),
            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                    restrict_xpaths='//span[@class="prev_next"]/a[@rel="next"]'
                ), follow=True),
        )

    def cleanText(self, str):
        soup = BeautifulSoup(str, 'html.parser')
        return re.sub(" +|\n|\r|\t|\0|\x0b|\xa0",' ',soup.get_text()).strip()


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
        posts = sel.xpath('//ol[@class="posts"]/li[@class="postbitlegacy postbitim postcontainer old"]')
        condition = "cancer"
        items = []
        topic = response.xpath('//h1/span[@class="threadtitle"]/a/text()').extract_first()
        url = response.url
        
        for post in posts:
            item = PostItemsList()
            item['author'] = post.xpath('.//div[@class="popupmenu memberaction"]/a/strong/text()').extract_first()
            item['author_link'] = post.xpath('.//div[@class="popupmenu memberaction"]/a/@href').extract_first()
            item['condition'] = condition
            item['create_date'] = self.getDate(post.xpath('.//span[@class="date"]/text()').extract_first().replace(',','').strip())
            item['domain'] = "".join(self.allowed_domains)
            item['post'] = re.sub(r'\s+',' ',self.cleanText(" ".join(post.xpath('.//div[@class="content"]//blockquote/text()').extract())))
            # item['tag']=''
            item['topic'] = topic
            item['url']=url
            items.append(item)
        return items
