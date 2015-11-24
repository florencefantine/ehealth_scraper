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

## LOGGING to file
#import logging
#from scrapy.log import ScrapyFileLogObserver

#logfile = open('testlog.log', 'w')
#log_observer = ScrapyFileLogObserver(logfile, level=logging.DEBUG)
#log_observer.start()

# Spider for crawling Adidas website for shoes
class ForumsSpider(CrawlSpider):
    name = "adhd_additudemag_spider"
    allowed_domains = ["additudemag.com"]
    start_urls = [
        "http://connect.additudemag.com/forums/viewforum/109/",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                    restrict_xpaths='//div[@class="topicTitle"]',
                    canonicalize=True,
                ), callback='parsePostsList'),
            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                    restrict_xpaths='//div[@class="forumName"]/a',
                    canonicalize=True,
                    deny=(r'user_profile_*\.html',)
                ), follow=True),
            Rule(LinkExtractor(
                    restrict_xpaths='//div[@class="paginate"]/a',
                    canonicalize=True,
                    deny=(r'user_profile_*\.html',)
                ), follow=True),
        )

    def cleanText(self,text,printableOnly=True):
        soup = BeautifulSoup(text,'html.parser')
        text = soup.get_text();
        text = re.sub("( +|\n|\r|\t|\0|\x0b|\xa0|\xbb|\xab)+",' ',text).strip()
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
        #posts = sel.css(".vt_post_holder")
        posts = sel.xpath('//table[@class="threadBorder"]')
        items = []
        topic = ''.join(sel.xpath('//div[@class="tableHeading"]/text()').extract())
        url = response.url
        condition="adhd"
        for post in posts:
            item = PostItemsList()
            item['author'] = self.cleanText(post.xpath('.//div[@class="largeLinks"]/a/text()').extract()[0])
            item['author_link'] = post.xpath('.//div[@class="largeLinks"]/a/@href').extract()[0]
            item['condition'] = condition
            create_date = getDate( cleanText( re.sub(r'(Posted:|\[|])','', ''.join(post.xpath('.//td[@class="tableRowHeading"]//text()').extract()) ).replace("Ignore","") ))
            item['create_date']= create_date
            item['post'] = self.cleanText(''.join(post.xpath('.//div[@class="post"]//text()').extract()))
            # item['tag']='adhd'
            item['topic'] = topic
            item['url']=url
            items.append(item)
        return items
