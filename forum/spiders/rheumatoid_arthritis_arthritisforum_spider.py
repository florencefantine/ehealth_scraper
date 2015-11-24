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
    name = "rheumatoid_arthritis_arthritisforum_spider"
    allowed_domains = ["arthritisforum.org.uk"]
#    start_urls = [
#        "http://www.healingwell.com/community/default.aspx?f=23&m=1001057",
#    ]
    start_urls = [
        "http://www.arthritisforum.org.uk/cgi-bin/showforum.pl",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                restrict_xpaths='/html/body/center/table[5]/tr/td/table[2]/tr',
                canonicalize=True,
                ), callback='parsePost', follow=True),
            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                restrict_xpaths="/html/body/center/a",
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

    # https://github.com/scrapy/dirbot/blob/master/dirbot/spiders/dmoz.py
    # https://github.com/scrapy/dirbot/blob/master/dirbot/pipelines.py
    def parsePost(self,response):
        logging.info(response)
        sel = Selector(response)
        posts = sel.xpath('/html/body/center/table[4]/tr/td/table[2]/tr')
        items = []
        if len(posts)==0:
            return items
        condition ="renal cell carcinoma"
        topic = response.xpath('/html/body/center/table[4]/tr/td/table[2]/tr[1]/td[2]/p[1]/text()[2]').extract()[0].strip()
        url = response.url
        for post in posts:
            item = PostItemsList()
            item['author'] = post.xpath("./td[1]/text()").extract()[3]
            item['author_link']=''
            item['condition'] = condition
            create_date= self.parseText(str=post.xpath('./td[1]/text()').extract()[1])
            item['create_date']= self.getDate(create_date)
            item['domain'] = "".join(self.allowed_domains)
            post_msg= self.parseText(str=post.xpath("./td[2]/p[2]").extract()[0])
            item['post']=post_msg
            item['tag']='rheumatoid arthritis'
            item['topic'] = topic
            item['url']=url
            logging.info(post_msg)
            items.append(item)
        return items

    def parseText(self, str):
        soup = BeautifulSoup(str, 'html.parser')
        return re.sub(" +|\n|\r|\t|\0|\x0b|\xa0",' ',soup.get_text()).strip()
        
