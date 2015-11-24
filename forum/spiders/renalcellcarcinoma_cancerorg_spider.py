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
    name = "renalcellcarcinoma_cancerorg_spider"
    allowed_domains = ["cancer.org"]
#    start_urls = [
#        "http://www.healingwell.com/community/default.aspx?f=23&m=1001057",
#    ]
    start_urls = [
        "http://csn.cancer.org/forum/142",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                restrict_xpaths='//tr[contains(@class, "odd")]//td[contains(@class, "title")]',
                canonicalize=True,
                ), callback='parsePost', follow=True),

            Rule(LinkExtractor(
                restrict_xpaths='//tr[contains(@class, "even")]//td[contains(@class, "title")]',
                canonicalize=True,
                ), callback='parsePost', follow=True),

            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                restrict_xpaths='//li[contains(@class, "pager-item")]',
                canonicalize=True,
                deny='http://csn.cancer.org/node/',
                #allow='http://www.cancerforums.net/threads/',
            ), follow=True),

            Rule(LinkExtractor(
                restrict_xpaths='//li[contains(@class, "pager-item")]',
                canonicalize=True,
                deny='http://csn.cancer.org/forum/'
                #allow='http://www.cancerforums.net/threads/',
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
        posts = sel.xpath('//*[@id="comments"]').css('.comment-forum')
        condition="renal cell carcinoma"
        items = []
        topic = self.cleanText(" ".join(sel.xpath('//*[@id="squeeze"]/div/div/h2/text()').extract()))
        url = response.url

        for post in posts:
            if len(post.css('.author'))==0:
                continue
            item = PostItemsList()
            item['author'] = self.cleanText(" ".join(post.css('.author').extract()))
            item['author_link']=''
            item['condition']=condition
            create_date = self.cleanText( " ".join(post.css('.date').xpath('./span/text()').extract()))
            item['create_date'] = self.getDate(create_date)
            post_msg=self.cleanText(" ".join(post.css('.content').extract()))
            item['post']=post_msg
            # item['tag']=''
            item['topic'] = topic
            item['url']=url
            logging.info(post_msg)
            items.append(item)
        return items

    def cleanText(self,text,printableOnly=True):
        soup = BeautifulSoup(text,'html.parser')
        text = soup.get_text();
        text = re.sub("(-+| +|\n|\r|\t|\0|\x0b|\xa0|\xbb|\xab)+",' ',text).strip()
        if(printableOnly):
            return filter(lambda x: x in string.printable, text)
        return text 

