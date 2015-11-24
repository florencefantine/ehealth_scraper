# -*- coding: utf-8 -*-

import hashlib
# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
import scrapy
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.selector import Selector
from forum.items import PostItemsList
import logging
import lxml.html
from lxml.etree import ParserError
from lxml.cssselect import CSSSelector
import re
from bs4 import BeautifulSoup
import urlparse
import string
import dateparser
import time

## LOGGING to file
#import logging
#from scrapy.log import ScrapyFileLogObserver

#logfile = open('testlog.log', 'w')
#log_observer = ScrapyFileLogObserver(logfile, level=logging.DEBUG)
#log_observer.start()

# Spider for crawling Adidas website for shoes
class ForumsSpider(CrawlSpider):
    name = "adhd_ning_spider"
    allowed_domains = ["adderworld.ning.com"]
    start_urls = [
        "http://adderworld.ning.com/forum/categories/general-1/listForCategory",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                    restrict_xpaths='//div[@class="xg_module_body"]//h3/a',
                    canonicalize=True,
                ), callback='parsePostsList'),
            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                    restrict_xpaths='//ul[@class="pagination easyclear "]/li[last()-1]/a',
                    canonicalize=True,
                ), follow=True),
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
            
    def urlRemove(self,url,keyToRemove):
        urlcomponents = urlparse.urlparse(url)
        params=urlparse.parse_qs(urlcomponents.query)
        newparams=""
        for key in params.keys():
            if not key==keyToRemove:
                newparams = newparams+ key+"="+params.get(key)[0]
        urlcomponents.query = newparams
        return urlparse.urlunparse(urlcomponents)

    def cleanText(self,text,printableOnly = True):
        soup = BeautifulSoup(text,'html.parser')
        text = soup.get_text();
        text = re.sub("( +|\n|\r|\t|\0|\x0b|\xa0|\xbb|\xab)+",' ',text).strip()
        if printableOnly:
            return filter(lambda x: x in string.printable, text)
        return text


    # http://adderworld.ning.com/forum/topics/what-every-adhd-child-deserves
    def parsePostsList(self,response):
        try:
            document = lxml.html.fromstring(response.body)
            document.make_links_absolute(base_url=response.url, resolve_base_href=True)
        except ParserError:
            return

        sel = Selector(response)
        posts = sel.xpath('//dl[@class="discussion clear i0 xg_lightborder"]')
        items = []
        topic = self.cleanText(response.xpath('//h1/text()').extract_first())
        url = response.url
        condition = "adhd"
        
        item = PostItemsList()
        item['author'] = response.xpath('//div[@class="xg_module xg_module_with_dialog"]//ul[@class="navigation byline"]/li/a[contains(@href,"profile")]/text()').extract_first()
        item['author_link'] = response.xpath('//div[@class="xg_module xg_module_with_dialog"]//ul[@class="navigation byline"]/li/a[contains(@href,"profile")]/@href').extract_first()
        item['condition']=condition
        item['create_date'] = self.getDate(self.cleanText(response.xpath('//div[@class="xg_module xg_module_with_dialog"]//ul[@class="navigation byline"]/li/a[@class="nolink"][2]/text()').extract_first().replace('on','').replace('in','').replace('at',','),False))
        item['post'] = re.sub('\s+',' '," ".join(response.xpath('//div[@class="xg_module xg_module_with_dialog"]//div[@class="xg_user_generated"]/p/text()').extract()).replace("\t","").replace("\n","").replace("\r",""))
        # item['tag']='epilepsy'
        item['topic'] = topic
        item['url']=url
        items.append(item)
        
        for post in posts:
            item = PostItemsList()
            item['author'] = post.xpath('./dt[@class="byline"]/a[contains(@href,"user")]/text()').extract_first()
            item['author_link'] = post.xpath('./dt[@class="byline"]/a[contains(@href,"user")]/@href').extract_first()
            item['condition']=condition
            item['create_date'] = self.getDate(self.cleanText(post.xpath('./dt[@class="byline"]/span[@class="timestamp"]/text()').extract_first().replace('at',','),False))
            item['post'] = re.sub('\s+',' '," ".join(post.xpath('.//div[@class="description"]/div[@class="xg_user_generated"]/p/text()').extract()).replace("\t","").replace("\n","").replace("\r",""))
            # item['tag']=''
            item['topic'] = topic
            item['url']=url
            items.append(item)
        return items
