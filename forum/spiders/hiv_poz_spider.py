# -*- coding: utf-8 -*-
import scrapy
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.selector import Selector
from forum.items import PostItemsList
from bs4 import BeautifulSoup
import re
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
    name = "hiv_poz_spider"
    allowed_domains = ["forums.poz.com"]
    start_urls = [
        "http://forums.poz.com/index.php?board=16.0",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                    restrict_xpaths='//table[@class="table_grid"]//span[contains(@id, "msg")]/a',
                ), callback='parsePostsList'),
            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                    restrict_xpaths='//div[@class="pagelinks"]/strong/following-sibling::a[1]'
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
            
    # https://github.com/scrapy/dirbot/blob/master/dirbot/spiders/dmoz.py
    # https://github.com/scrapy/dirbot/blob/master/dirbot/pipelines.py
    def parsePostsList(self,response):
        sel = Selector(response)
        posts = sel.xpath('//div[contains(@class, "windowbg")]')
        items = []
        condition = 'hiv'
        topic = response.xpath('//div[@class="navigate_section"]//li[@class="last"]//span/text()').extract_first()
        url = response.url

        for post in posts:
            item = PostItemsList()
            item['author'] = post.xpath('.//div[@class="poster"]/h4/a/text()').extract_first()
            if item['author']:
                item['author_link'] = post.xpath('.//div[@class="poster"]/h4/a/@href').extract_first()
                item['condition'] = condition
                create_date = self.cleanText(post.xpath('.//div[@class="keyinfo"]/div[@class="smalltext"]/text()').extract()[1])
                item['create_date'] = self.getDate(create_date)
                item['post'] = self.cleanText(" ".join(post.xpath('.//div[@class="post"]/div[@class="inner"]/text()').extract()))
                item['topic'] = topic
                item['url']=url
                items.append(item)
        return items
