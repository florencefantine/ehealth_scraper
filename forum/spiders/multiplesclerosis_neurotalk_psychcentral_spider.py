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
## LOGGING to file
#import logging
#from scrapy.log import ScrapyFileLogObserver

#logfile = open('testlog.log', 'w')
#log_observer = ScrapyFileLogObserver(logfile, level=logging.DEBUG)
#log_observer.start()


# Spider for crawling multiple-sclerosis board
class ForumsSpider(CrawlSpider):
    name = "multiplesclerosis_neurotalk_psychcentral_spider"
    allowed_domains = ["neurotalk.psychcentral.com"]
    start_urls = [
        "http://neurotalk.psychcentral.com/forum17.html",
    ]

    rules = (
            Rule(LinkExtractor(
                restrict_xpaths='//*/a[starts-with(@id, "thread_title_")]',
                canonicalize=True,
                allow='http://neurotalk\.psychcentral\.com/.*thread.*',
                ), callback='parsePost', follow=True),
            # Rule to follow arrow to next grid
            Rule(LinkExtractor(
                restrict_xpaths='//*/a[starts-with(@title,"Next Page")]',
            ), callback='parsePost', follow=True),
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
        posts = sel.xpath('//*/table[starts-with(@id,"post")]')
        items = []
        condition=  "multiple sclerosis"
        if not posts: return items
        topic = self.cleanText(response.xpath('/html/body/table[2]/tr/td/h3').extract()[0].encode('ascii'))
        url = response.url
        for post in posts:
            post_xp = post.xpath('./tr[2]/td[2]/div[2]')
            if not post_xp: continue
            post_msg = self.cleanText(" ".join(post_xp.extract()))

            item = PostItemsList()
            item['author'] = self.cleanText(post.xpath('./tr[2]/td[1]/div[starts-with(@id,"postmenu")]/a').extract()[0].encode('ascii'))
            item['author_link'] = "http://neurotalk.psychcentral.com/%s" % post.xpath('./tr[2]/td[1]/div[starts-with(@id,"postmenu")]/a/@href').extract()[0]
            item['condition'] = condition
            create_date = self.cleanText(" ".join(post.xpath('./tr/td[1]').extract()))
            item['create_date'] = self.getDate(create_date)
            item['post'] = post_msg
            # item['tag'] = 'multiple-sclerosis'
            item['topic'] = topic
            item['url'] = url
            #logging.info(post_msg)
            items.append(item)

        return items

