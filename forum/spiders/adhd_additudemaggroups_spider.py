# -*- coding: utf-8 -*-
import scrapy
import hashlib
import string
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
    name = "adhd_additudemaggroup_spider"
    allowed_domains = ["additudemag.com"]
    start_urls = [
        "http://connect.additudemag.com/groups/all_topics/",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                    restrict_xpaths='//a[contains(@href,"additudemag.com/groups/topic/")]',
                    canonicalize=True,
                ), callback='parsePostsList'),
            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                    restrict_xpaths='//div[@class="paginate"]/a',
                    canonicalize=True,
                    deny=(r'user_profile_*\.html',)
                ), follow=True),
        )

    def cleanText(self,text,printableOnly = True):
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
            
    # http://connect.additudemag.com/groups/topic/Best_advise_for_son_dealing_with_depression/
    def parsePostsList(self,response):
        sel = Selector(response)
        #posts = sel.css(".vt_post_holder")
        posts = sel.xpath('//div[@class="comment"]')
        items = []
        topic = ''.join(sel.xpath('//h5//text()').extract())
        url = response.url
        condition="adhd"
            
        author = sel.xpath('.//span[@class="post-meta"]//a/text()').extract_first()
        author_link = sel.xpath('.//span[@class="post-meta"]//a/@href').extract_first()
        create_date = ''.join(sel.xpath('.//span[@class="post-meta"]/text()').extract()).replace("Posted by","").replace("to","")

        if author and author_link and create_date!='':
            item = PostItemsList()
            item['author'] = author
            item['author_link'] = author_link
            item['condition'] = condition
            item['create_date']= self.getDate(self.cleanText(create_date.replace("|","").replace("on","").replace("at","")))
            item['post'] = self.cleanText(''.join(sel.xpath('.//div[@class="blog-post"]/p/text()').extract()))
            item['topic'] = topic
            item['url']=url
            items.append(item)

        for post in posts:
            author = post.xpath('.//span[@class="comment-meta"]//a[0]/text()').extract()
            author_link = post.xpath('.//span[@class="comment-meta"]//a[0]/@href').extract()
            create_date = self.cleanText(''.join(post.xpath('.//span[@class="comment-meta"]/text()').extract()).replace("|","").replace("on","").replace("at",""))
            if author and author_link and create_date!='':
                item = PostItemsList()
                item['author'] = author
                item['author_link'] = author_link
                item['condition'] = condition
                item['create_date']= self.getDate(create_date)
                item['post'] = self.cleanText(message = ''.join(post.xpath('.//div[@class="comment-text"]/text()').extract()))
                item['topic'] = topic
                item['url']=url
                items.append(item)
        return items
