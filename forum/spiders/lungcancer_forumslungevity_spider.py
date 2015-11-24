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
    name = "lungcancer_forumslungevity_spider"
    allowed_domains = ["lungevity.org"]
    start_urls = [
        "http://forums.lungevity.org/index.php?/forum/19-general/",
        
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                    restrict_xpaths='//a[@class="topic_title"]',
                    canonicalize=False,
                ), callback='parsePostsList'),
            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                    restrict_xpaths='//li[@class="next"]',
                    canonicalize=False,
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
            
    def cleanText(self,text,printableOnly=True):
        soup = BeautifulSoup(text,'html.parser')
        text = soup.get_text();
        text = re.sub("(-+| +|\n|\r|\t|\0|\x0b|\xa0|\xbb|\xab)+",' ',text).strip()
        if(printableOnly):
            return filter(lambda x: x in string.printable, text)
        return text 

    def parsePostsList(self,response):
        sel = Selector(response)
        #posts = sel.css(".vt_post_holder")
        posts = sel.xpath('//div[@class="post_wrap"]')
        items = []
        topic = ''.join(sel.xpath('//h1[@class="ipsType_pagetitle"]/text()').extract())
        url = response.url
        condition="lung cancer"
        for post in posts:
            item = PostItemsList()
            item['author'] = self.cleanText(''.join(post.xpath('.//span[@class="author vcard"]/text()').extract()))
            item['author_link'] = ''
            item['condition'] = condition
            item['create_date'] = self.getDate(''.join(post.xpath('.//abbr[@class="published"]/text()').extract()))
            
            message = ''.join(post.xpath('.//div[@class="post entry-content "]//text()').extract())
            item['post'] = self.cleanText(message)
            item['topic'] = topic
            item['url']=url
            items.append(item)
        return items
