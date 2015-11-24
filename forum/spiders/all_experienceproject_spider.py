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
import time
import dateparser
import time

class ForumsSpider(CrawlSpider):
    name = "all_experienceproject_spider"
    allowed_domains = ["www.experienceproject.com"]
    start_urls = [
        "http://www.experienceproject.com/groups",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                    restrict_xpaths='//div[@class="group-name"]/a', 
                ), callback='parsePostsList'),
            # Rule to follow arrow to next product grid
            #Rule(LinkExtractor(
            #        restrict_xpaths='//td[@class="msgSm" and @align="right"]/b/strong/following-sibling::a[1]'
            #    ), follow=True),
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
            
    # def getDate(self,date_str):
    #     result1 = re.compile(r"^[a-zA-Z][a-zA-Z][a-zA-Z]\s\d+$").match(date_str)
    #     result2=re.compile(r"^\d+\s(hours|hrs) ago").match(date_str)
    #     if result1:
    #         return date_str+", 2015"
    #     elif result2:
    #         return time.strftime("%b %d, %Y")
    #     else:
    #         return date_str


    def cleanText(self,text,printableOnly=True):
        soup = BeautifulSoup(text,'html.parser')
        text = soup.get_text();
        text = re.sub("( +|\n|\r|\t|\0|\x0b|\xa0|\xbb|\xab)+",' ',text).strip()
        if(printableOnly):
            return filter(lambda x: x in string.printable, text)
        return text 


    def parsePostsList(self,response):
        sel = Selector(response)
        posts = sel.xpath('//div[@class="expression  titled-story-expression  story-expression  is-link "]/div[@class="expression-content"]')
        items = []
        topic = response.xpath('//h1[@class="group-title"]/a/text()').extract_first().strip()
        url = response.url
        
        for post in posts:
            item = PostItemsList()
            item['author'] = post.xpath('.//span[@class="member-username-with-status"]/a[@class="member-username  profile-hoverlay-enabled"]/text()').extract_first()
            if item['author']:
                item['author_link'] = post.xpath('.//span[@class="member-username-with-status"]/a[@class="member-username  profile-hoverlay-enabled"]/@href').extract_first()
                item['create_date'] =self.getDate(" ".join(post.xpath('.//span[@class="date"]/span[@class="model-create-date"]/text()').extract()).strip())
                item1 = self.cleanText(" ".join(post.xpath('.//div[@class="content"]/h2/a/text()').extract()))
                item2 = self.cleanText(" ".join(post.xpath('.//div[@class="content"]/span/text()').extract()))
                item['post'] = item1 + ' ' + item2
                item['topic'] = self.cleanText(topic)
                item['url']=url
                items.append(item)
        return items
