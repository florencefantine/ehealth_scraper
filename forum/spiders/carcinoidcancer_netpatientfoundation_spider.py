# -*- coding: utf-8 -*-
import scrapy
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
    name = "carcinoidcancer_netpatientfoundation_spider"
    allowed_domains = ["netpatientfoundation.org"]
#    start_urls = [
#        "http://www.healingwell.com/community/default.aspx?f=23&m=1001057",
#    ]
    start_urls = [
        "http://www.netpatientfoundation.org/forum/5_1.html",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                restrict_xpaths='//tr[contains(@class, "tbCel1")]/td[2]',
                canonicalize=True,
                ), callback='parsePost'),

            Rule(LinkExtractor(
                restrict_xpaths='//tr[contains(@class, "tbCel2")]/td[2]',
                canonicalize=True,
                ), callback='parsePost'),

            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                restrict_xpaths='/html/body/div[3]/table[5]/tr/td/span/b/a[contains(@class, "navCell")]',
            ), follow=True),
            
            Rule(LinkExtractor(
                restrict_xpaths='/html/body/div[3]/table[4]/tr/td/span/b/a[contains(@class, "navCell")]'
            ), callback='parsePost')
        )

    def cleanText(self,text):
        soup = BeautifulSoup(text,'html.parser')
        text = soup.get_text();
        text = re.sub("( +|\n|\r|\t|\0|\x0b|\xa0|\xbb|\xab)+",' ',text).strip()
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
    def parsePost(self,response):
        logging.info(response)
        sel = Selector(response)
        posts = sel.xpath("//*[@id=\"allMsgs\"]").css(".forumsmb")
        condition="carcinoid cancer"
        items = []
        topic = response.xpath('//h1[contains(@class, "headingTitle")]/text()').extract()[0]
        url = response.url
        for post in posts:
            item = PostItemsList()
            item['author'] = post.css('.username').xpath("./a/text()").extract()[0]
            item['author_link']=response.urljoin(post.css('.username').xpath("./a/@href").extract()[0])
            item['condition']=condition
            create_date= re.sub(" +|\n|\r|\t|\0|\x0b|\xa0",' ',post.xpath('./tr[1]/td[3]/div/text()').extract()[1]).replace("Posted:","").strip()
            item['create_date']= self.getDate(create_date)
            item['post']=self.cleanText(post.css('.postedText').xpath('text()').extract()[0])
            item['topic'] = topic
            item['url']=url
            items.append(item)
        return items
