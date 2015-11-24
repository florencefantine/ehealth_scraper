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
    name = "cancer_macmillan_spider"
    allowed_domains = ["macmillan.org.uk"]
    start_urls = [
        "https://community.macmillan.org.uk/cancer_types/neuroendocrine-cancer/discussions?ThreadSortBy=Subject&SortOrder=Ascending",
        "https://community.macmillan.org.uk/cancer_types/breast-cancer/discussions?pi1116=1",
        "https://community.macmillan.org.uk/cancer_types/lung-cancer/discussions",
        "https://community.macmillan.org.uk/cancer_types/non-hodgkin-lymphoma/discussions",
        "https://community.macmillan.org.uk/cancer_types/prostate-cancer/discussions"
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                restrict_xpaths='//a[contains(@class,"view-post")]',
                canonicalize=True,
                deny='http://www.dailystrength.org/people/',
                ), callback='parsePost', follow=True),

            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                restrict_xpaths='//div[contains(@class, "page")]',
                canonicalize=True,
                #allow='http://www.cancerforums.net/threads/',
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
        posts = sel.css('.content-item')
        items = []
        topic = " ".join(sel.css('.forum-stats-container').xpath('./h1/text()').extract())
        condition="cancer"
        url = response.url
        for post in posts:
            item = PostItemsList()
            item['author'] = self.parseText(" ".join(post.css('.user-name').xpath('./a').extract()))
            item['author_link']=response.urljoin(post.css('.user-name').xpath('./a/@href').extract()[0])
            item['condition']=condition
            create_date = self.parseText(post.css('.post-date').extract()[0]).replace("on","").strip()
            item['create_date'] = self.getDate(create_date)
            item['domain'] = "".join(self.allowed_domains)
            post_msg=self.parseText(str=post.css('.post-content ').extract()[0])
            item['post']=post_msg
            # item['tag']=''
            item['topic'] =self.parseText(topic)
            item['url']=url
            logging.info(post_msg)
            items.append(item)
        return items

    def parseText(self, str):
        soup = BeautifulSoup(str, 'html.parser')
        return re.sub(" +|\n|\r|\t|\0|\x0b|\xa0",' ',soup.get_text()).strip()
