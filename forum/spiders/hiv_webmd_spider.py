# -*- coding: utf-8 -*-
import scrapy
import hashlib
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.selector import Selector
from forum.items import PostItemsList
import re
import logging
from bs4 import BeautifulSoup
import string
import dateparser
import time
# import lxml.html
# from lxml.etree import ParserError
# from lxml.cssselect import CSSSelector

## LOGGING to file
#import logging
#from scrapy.log import ScrapyFileLogObserver

#logfile = open('testlog.log', 'w')
#log_observer = ScrapyFileLogObserver(logfile, level=logging.DEBUG)
#log_observer.start()

# Spider for crawling Adidas website for shoes
class ForumsSpider(CrawlSpider):
    name = "hiv_webmd_spider"
    allowed_domains = ["webmd.com"]
#    start_urls = [
#        "http://www.healingwell.com/community/default.aspx?f=23&m=1001057",
#    ]
    start_urls = [
        "http://exchanges.webmd.com/hiv-and-aids-exchange/forum/index",
        "http://exchanges.webmd.com/hiv-and-aids-exchange/tip/index",
        "http://exchanges.webmd.com/hiv-and-aids-exchange/resource/index"
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                restrict_xpaths='//div[contains(@class, "expert_fmt")]/span',
                canonicalize=True,
                ), callback='parsePost', follow=True),

            Rule(LinkExtractor(
                restrict_xpaths='//div[contains(@class, "pages")]',
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
            
    def cleanText(self,text,printableOnly=True):
        soup = BeautifulSoup(text,'html.parser')
        text = soup.get_text();
        text = re.sub("(-+| +|\n|\r|\t|\0|\x0b|\xa0|\xbb|\xab)+",' ',text).strip()
        if(printableOnly):
            return filter(lambda x: x in string.printable, text)
        return text 

    def parsePost(self,response):
        logging.info(response)
        sel = Selector(response)
        posts = sel.xpath('//div[contains(@class, "exchange_thread_reply_rdr")]')
        items = []
        if len(sel.xpath('//div[contains(@class, "first_item_title_fmt")]'))==0:
            return items
        topic = sel.xpath('//div[contains(@class, "first_item_title_fmt")]/text()').extract()[0]
        url = response.url
        condition="hiv"
        post = sel.xpath('//div[contains(@class, "firstitem_mid_fmt")]')
        item = PostItemsList()
        if len(post.css('.post_hdr_fmt').xpath('./a'))>0:
            item['author'] = post.css('.post_hdr_fmt').xpath("./a").xpath("text()").extract()[0].strip()
            item['author_link']=response.urljoin(post.css('.post_hdr_fmt').xpath("./a/@href").extract()[0])
        else:
            item['author'] = ""
            item['author_link']=""
        date = post.css('.first_posted_fmt').extract()[0]
        date = date[date.find('DateDelta')+11:date.rfind("'")]
        item['condition'] = condition
        item['create_date'] = self.getDate(date)
        item['domain'] = "".join(self.allowed_domains)
        # soup = BeautifulSoup(post_msg, 'html.parser')
        # post_msg = re.sub(" +|\n|\r|\t|\0|\x0b|\xa0",' ',soup.get_text()).strip()
        item['post']=self.cleanText(post.css('.post_fmt').extract()[0])
        # item['tag']=''
        item['topic'] = topic
        item['url']=url
        items.append(item)

        for post in posts:
            item = PostItemsList()
            if len(post.css('.post_hdr_fmt'))==0:
                continue
            if len(post.css('.post_hdr_fmt').xpath('./a'))>0:
                item['author'] = post.css('.post_hdr_fmt').xpath("./a").xpath("text()").extract()[0].strip()
                item['author_link']=response.urljoin(post.css('.post_hdr_fmt').xpath("./a/@href").extract()[0])
            else:
                item['author'] = ""
                item['author_link']=""
            date = post.css('.posted_fmt').extract()[0]
            date = date[date.find('DateDelta')+11:date.rfind("'")]
            item['condition'] = condition
            item['create_date'] = self.getDate(date)
            # soup = BeautifulSoup(post_msg, 'html.parser')
            # post_msg = re.sub(" +|\n|\r|\t|\0|\x0b|\xa0",' ',soup.get_text()).strip()
            item['post']=self.cleanText(post.css('.post_fmt').extract()[0])
            # item['tag']='hiv'
            item['topic'] = topic
            item['url']=url
            items.append(item)
        return items
