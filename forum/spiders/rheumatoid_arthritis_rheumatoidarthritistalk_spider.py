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
    name = "rheumatoid_arthritis_rheumatoidarthritistalk_spider"
    allowed_domains = ["rheumatoidarthritistalk.com"]
#    start_urls = [
#        "http://www.healingwell.com/community/default.aspx?f=23&m=1001057",
#    ]
    start_urls = [
        "http://rheumatoidarthritistalk.com/forums/lounge.2/",
        "http://rheumatoidarthritistalk.com/forums/introductions.3/",
        "http://rheumatoidarthritistalk.com/forums/procedures-tests.4/",
        "http://rheumatoidarthritistalk.com/forums/medications-and-natural-herbal-remedies.5/",
        "http://rheumatoidarthritistalk.com/forums/living-with-rheumatoid-arthritis.6/",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                restrict_xpaths='//div[contains(@class,"titleText")]/h3',
                canonicalize=True,
                ), callback='parsePost', follow=True),
            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                restrict_xpaths="//div[contains(@class, 'PageNav')]",
            ), callback='parsePost', follow=True),
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
        posts = sel.css(".messageList").xpath('./li')
        items = []
        condition = 'rheumatoid arthritis'
        if len(posts)==0:
            return items
        topic = sel.css('.titleBar').xpath('./h1/text()').extract()[0].strip()
        url = response.url
        for post in posts:
            item = PostItemsList()
            if len(post.css('.userText'))>0:
                item['author'] = post.css('.userText').xpath('./a/text()').extract()[0]
                item['author_link']=response.urljoin(post.css('.userText').xpath('./a/@href').extract()[0])
            else:
                continue
            create_date= self.parseText(str=post.css('.DateTime').extract()[0])
            item['create_date']= self.getDate(create_date)
            post_msg= self.parseText(str=post.css('.messageText').extract()[0])
            item['post']=post_msg
            # item['tag']='rheumatoid arthritis'
            item['topic'] = topic
            item['url']=url
            items.append(item)
        return items

    def parseText(self, str):
        soup = BeautifulSoup(str, 'html.parser')
        return re.sub(" +|\n|\r|\t|\0|\x0b|\xa0",' ',soup.get_text()).strip()
