#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import hashlib
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
## LOGGING to file
#import logging
#from scrapy.log import ScrapyFileLogObserver

#logfile = open('testlog.log', 'w')
#log_observer = ScrapyFileLogObserver(logfile, level=logging.DEBUG)
#log_observer.start()


# Spider for crawling multiple-sclerosis board
class ForumsSpider(CrawlSpider):
    name = "multiplesclerosis_webmd_spider"
    allowed_domains = ["exchanges.webmd.com", "forums.webmd.com"]
    start_urls = [
        "http://exchanges.webmd.com/multiple-sclerosis-exchange/forum/index",
    ]

    rules = (
            # topics
            Rule(LinkExtractor(
                #restrict_xpaths='//*[@class="bottomlinks_fmt"]',
                canonicalize=True,
                allow='http://forums\.webmd\.com/3/multiple\-sclerosis\-exchange/forum/.*',
            ), callback='parsePost'),
            # rule to follow arrow to next grid
            Rule(LinkExtractor(
                restrict_xpaths='//*[@id="Pagination2_Next"]',
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
            
    def parsePost(self,response):
        #logging.info(response)
        sel = Selector(response)
        posts = sel.xpath('//*/div[@class="thread_fmt"]')
        items = []
        condition = "multiple sclerosis"
        if not posts: return items
        topic = self.cleanText(response.xpath('//*/div[@class="first_item_title_fmt"]').extract()[0].encode('ascii'))
        url = response.url
        for post in posts:
            post_xp = post.xpath('./div[3]')
            if not post_xp: continue
            post_msg = self.cleanText(str=post_xp.extract()[0])

            item = PostItemsList()
            item['author'] = self.cleanText(post.xpath('./*/a[1]').extract()[0].encode('ascii'))
            item['author_link'] = post.xpath('./*/a[1]/@href').extract()[0]
            #create_date_xp = post.xpath('//*[@class="vt_reply_timestamp"]')
            if posts.index(post) != 0:
                create_date_js = post.xpath('./div[@class="posted_fmt"]/script').extract()[0]
            else:
                create_date_js = sel.xpath('//*/div[@class="first_posted_fmt"]/script').extract()[0]
            create_date = create_date_js.replace("""<script type="text/javascript">document.write(DateDelta('""",'')
            create_date = create_date.replace("""'));</script>""",'')
            item['condition'] = condition
            item['create_date'] = self.getDate(create_date)
            item['post'] = post_msg
            # item['tag'] = ''
            item['topic'] = topic
            item['url'] = url
            #logging.info(post_msg)
            items.append(item)

        return items

