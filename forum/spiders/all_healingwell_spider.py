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

# # LOGGING to file
# import logging
# from scrapy.log import ScrapyFileLogObserver

# logfile = open('testlog.log', 'w')
# log_observer = ScrapyFileLogObserver(logfile, level=logging.DEBUG)
# log_observer.start()

# Spider for crawling Adidas website for shoes

# epilepsy, etc
class ForumsSpider(CrawlSpider):
    name = "all_healingwell_spider"
    allowed_domains = ["www.healingwell.com"]
    start_urls = [
        "http://www.healingwell.com/community/default.aspx?f=23&m=1001057"
        ,"http://www.healingwell.com/community/?f=10"
        ,"http://www.healingwell.com/community/default.aspx?f=25"
        ,"http://www.healingwell.com/community/?f=35"
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                restrict_xpaths='//tr/td[contains(@class,"TopicTitle")]/a',
                canonicalize=True,
                ), callback='parsePost'),
            # Rule to follow arrow to next product grid
            # Rule(LinkExtractor(
            #    restrict_xpaths="//tr[td[contains(., 'forums')]][last()]/td[contains(., 'forums')]/br/a",
            # ), follow=True),
            Rule(LinkExtractor(
                restrict_xpaths='//a',
                canonicalize=True,
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
            
    # def getDate(self,date_str):
    #     # '7/11/2014 3:22 PM (GMT -7)'
    #     result1 = re.compile(r"^yesterday").match(date_str)
    #     result2=re.compile(r"^today").match(date_str)
    #     yesterday = date.today() - timedelta(1)
    #     if result1:
    #         # 'create_date': u'Yesterday 10:51 AM (GMT -7)',
    #         return time.strftime("%m/%d/%Y ")+date_str.replace("yesterday")
    #     elif result2:
    #         return yestrday.strftime("%m/%d/%Y ")+date_str.replace("today")
    #     else:
    #         return date_str

    # https://github.com/scrapy/dirbot/blob/master/dirbot/spiders/dmoz.py
    # https://github.com/scrapy/dirbot/blob/master/dirbot/pipelines.py
    def parsePost(self, response):
        logging.info(response)
        sel = Selector(response)
        posts = sel.css("Table.PostBox")
        breadcrumbs = sel.css("#Breadcrumbs")
        # condition = breadcrumbs.xpath("./a[3]/text()")
        condition = breadcrumbs.xpath("./a[3]/text()").extract()[0].lower()
        items = []
        topic = response.xpath('//div[contains(@id,"PageTitle")]/h1/text()').extract()[0]
        url = response.url
        for post in posts:
            item = PostItemsList()
            item['author'] = post.css('.msgUser').xpath("./a[2]").xpath("text()").extract()[0]
            item['author_link'] = post.css('.msgUser').xpath("./a[2]/@href").extract()[0]
            item['condition'] = condition.lower()
            item['create_date'] = self.getDate(re.sub(" +|\n|\r|\t|\0|\x0b|\xa0", ' ', response.css('td.msgThreadInfo').xpath('text()').extract()[0].replace("Posted ","")).strip().lower())
            post_msg = self.cleanText(post.css('.PostMessageBody').extract()[0])
            item['post'] = post_msg
            # item['tag'] = ''
            item['topic'] = topic
            item['url'] = url
            items.append(item)
        return items
