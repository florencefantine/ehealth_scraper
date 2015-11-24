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

class ForumsSpider(CrawlSpider):
    name = "hepc_hepcukforum_spider"
    allowed_domains = ["www.hepcukforum.org"]
    start_urls = [
        "http://www.hepcukforum.org/phpBB2/viewforum.php?f=1&sid=da54cd4e2f79318463ea37a3e6c8c61a",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                    restrict_xpaths='//a[@class="topiclink"]', 
                ), callback='parsePostsList'),
            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                    restrict_xpaths='//div[@class="pagination"]/a[contains(text(), "Next")]'
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
        posts = sel.xpath('//table[@class="post"]')
        items = []
        condition = "hepatitis c"
        topic = response.xpath('//table[@class="hdr"][1]//td[@nowrap="nowrap"]/text()').extract_first()
        url = response.url
        
        for post in posts:
            item = PostItemsList()
            item['author'] = post.xpath('.//span[@class="name"]/text()').extract_first()
            if item['author']:
                item['author_link'] = ''
                item['condition'] = condition
                create_date = post.xpath('.//span[@class="postdate"]/text()').extract_first().replace(u'Posted:','').strip()
                item['create_date'] = self.getDate(create_date)
                item['domain'] = "".join(self.allowed_domains)
                item['post'] = self.cleanText(" ".join(post.xpath('.//div[@class="postbody"]/text()').extract()))
                # item['tag']=''
                item['topic'] = topic.strip()
                item['url']=url
                items.append(item)
        return items
