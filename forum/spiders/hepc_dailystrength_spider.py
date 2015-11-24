# -*- coding: utf-8 -*-
import scrapy
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

class ForumsSpider(CrawlSpider):
    name = "hepc_dailystrength_spider"
    allowed_domains = ["www.dailystrength.org"]
    start_urls = [
        "http://www.dailystrength.org/c/Hepatitis-C/forum",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                    restrict_xpaths='//tr[contains(@class, "sectiontableentry")]//a[@class="strong"]', 
                ), callback='parsePostsList'),
            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                    restrict_xpaths='//table[@class="davetest"]/tr[3]//a[text(), "next"]'
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
            
    def parsePostsList(self,response):
        sel = Selector(response)
        posts = sel.xpath('//table[@class="reply_table"]/tr')
        items = []
        condition="hepatitis c"
        topic = response.xpath('//div[@class="discussion_topic_header_subject"]/text()').extract_first()
        url = response.url

        item = PostItemsList()
        item['author'] = self.cleanText(response.xpath('.//p[@class="username"]/a/text()').extract_first())
        item['author_link'] = response.xpath('.//p[@class="username"]/a/@href').extract_first()
        item['condition'] = condition
        create_date = response.xpath('.//div[contains(@class, "discussion_text")]/span/text()').extract_first().replace(u'Posted on','').strip()  
        item['create_date'] = self.getDate(create_date)
        item['post'] = self.cleanText(" ".join(response.xpath('.//div[contains(@class, "discussion_text")]/text()').extract()))
        item['topic'] = topic.strip()
        item['url']=url
        logging.info(item.__str__)
        items.append(item)
        
        for post in posts:
            item = PostItemsList()
            item['author'] = post.xpath('.//p[@class="username"]/a/text()').extract_first()
            if item['author']:
                item['author'] = item['author'].strip()
                item['author_link'] = post.xpath('.//p[@class="username"]/a/@href').extract_first()
                item['condition'] = condition
                create_date = post.xpath('.//span[@class="graytext"][2]/text()').extract_first().strip()
                item['create_date'] = self.getDate(create_date)
                item['post'] = self.cleanText(" ".join(post.xpath('.//div[contains(@class, "discussion_text")]/text()').extract()))
                item['topic'] = topic.strip()
                item['url']=url
                items.append(item)
        return items
