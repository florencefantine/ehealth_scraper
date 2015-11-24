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
    name = "adhd_dailystrength_spider"
    allowed_domains = ["dailystrength.org"]
#    start_urls = [
#        "http://www.healingwell.com/community/default.aspx?f=23&m=1001057",
#    ]
    start_urls = [
        "http://www.dailystrength.org/c/Parents-of-Children-With-ADHD/forum",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                restrict_xpaths='//tr[contains(@class, "sectiontableentry2")]',
                canonicalize=True,
                deny='http://www.dailystrength.org/people/',
                ), callback='parsePost', follow=True),
            Rule(LinkExtractor(
                restrict_xpaths='//tr[contains(@class, "sectiontableentry1")]',
                deny='http://www.dailystrength.org/people/',
                canonicalize=True,
                ), callback='parsePost'),

            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                restrict_xpaths='//a[contains(@class, "medium")]',
                deny='http://www.dailystrength.org/people/',
                canonicalize=True,
            ), follow=True),
            # Rule(LinkExtractor(
            #     restrict_xpaths='//*[@id="col1"]/div[2]/div[2]/div[1]/table/tr[3]/td[1]/a[1]/@href',
            # ), follow=True),
        )

    def cleanText(self,text, printableOnly =True):
        soup = BeautifulSoup(text,'html.parser')
        text = soup.get_text();
        text = re.sub("( +|\n|\r|\t|\0|\x0b|\xa0|\xbb|\xab)+",' ',text).strip()
        if printableOnly:
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
            
    # http://www.dailystrength.org/c/Parents_of_Children_With_ADHD/forum/20424235-anyone-relate-any
    def parsePost(self,response):
        logging.info(response)
        sel = Selector(response)
        posts = sel.xpath('//*[@id="col1"]/div[2]/div[2]/div[1]/table[4]')
        items = []
        condition="adhd"
        topic = sel.xpath('//div[contains(@class, "discussion_topic_header_subject")]/text()').extract()[0]
        url = response.url
        post = sel.xpath('//table[contains(@class, "discussion_topic")]')
        item = PostItemsList()
        item['author'] = post.css('.username').xpath("./a").xpath("text()").extract()[0].strip()
        item['author_link']=response.urljoin(post.css('.username').xpath("./a/@href").extract()[0])
        item['condition']=condition
        item['create_date']= self.getDate(self.cleanText(post.css('.discussion_text').xpath('./span/text()').extract()[0]))
        item['domain'] = "".join(self.allowed_domains)
        post_msg=self.cleanText(" ".join(post.css('.discussion_text').extract()))
        item['post']=post_msg
        # item['tag']=condition
        item['topic'] = topic
        item['url']=url
        logging.info(post_msg)
        items.append(item)

        for post in posts:
            item = PostItemsList()
            if len(post.css('.username')) == 0:
                continue
            item['author'] = post.css('.username').xpath("./a").xpath("text()").extract()[0].strip()
            item['author_link']=response.urljoin(post.css('.username').xpath("./a/@href").extract()[0])
            item['create_date']= self.getDate(self.cleanText(" ".join(post.xpath('./tr[1]/td[2]/div/table/tr/td/span[2]/text()').extract())))
            item['domain'] = "".join(self.allowed_domains)
            item['post']=self.cleanText(" ".join(post.css('.discussion_text').extract()))
            # item['tag']=''
            item['topic'] = topic
            item['url']=url
            logging.info(post_msg)
            items.append(item)
        return items
