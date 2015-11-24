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
    name = "rheumatoid_arthritis_wellescent_spider"
    allowed_domains = ["wellescent.com"]
#    start_urls = [
#        "http://www.healingwell.com/community/default.aspx?f=23&m=1001057",
#    ]
    start_urls = [
        "http://wellescent.com/health_forum/forum-30140-background_information_on_rheumatoid_arthritis.html",
        "http://wellescent.com/health_forum/forum-30146-rheumatoid_arthritis_treatments_medications_and_side_effects.html",
        "http://wellescent.com/health_forum/forum-30147-new_research_on_rheumatoid_arthritis.html",
        "http://wellescent.com/health_forum/forum-30144-living_and_coping_with_rheumatoid_arthritis.html",
        "http://wellescent.com/health_forum/forum-30148-rheumatoid_arthritis_and_relationships.html",
        "http://wellescent.com/health_forum/forum-30150-rheumatoid_arthritis_and_work_life.html",
        "http://wellescent.com/health_forum/forum-30142-fitness_and_exercise_with_rheumatoid_arthritis.html",
        "http://wellescent.com/health_forum/forum-30143-leisure_with_rheumatoid_arthritis.html",
        "http://wellescent.com/health_forum/forum-30141-rheumatoid_arthritis_and_child_rearing.html",
        "http://wellescent.com/health_forum/forum-30149-travel_and_rheumatoid_arthritis.html",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                restrict_xpaths='//*[@id="content"]/table/tr/td[3]/div/span/a[2]',
                canonicalize=True,
                ), callback='parsePost', follow=True),
            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                restrict_xpaths="//div[contains(@class, 'pagination')]",
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
        posts = sel.xpath('.//*[@id="posts"]/table')
        items = []
        if len(posts)==0:
            return items
        topic = sel.xpath('.//*[@id="posts"]/table[1]/tr[2]/td[2]/table/tr/td/div[1]/b/text()').extract()[0]
        url = response.url
        condition = 'rheumatoid arthritis'
        for post in posts:
            item = PostItemsList()
            item['author'] = post.xpath("./tr[2]/td[1]/strong/span/text()").extract()[0]
            item['author_link']=''
            item['condition'] = condition
            create_date= self.parseText(str=post.xpath('./tr[1]//span/strong/text()').extract()[1])
            item['create_date']= self.getDate(create_date)
            item['domain'] = "".join(self.allowed_domains)
            post_msg= self.parseText(str=post.xpath('./tr[2]/td[2]/table/tr/td/div[1]/div').extract()[0])
            item['post']=post_msg
            # item['tag']='rheumatoid arthritis'
            item['topic'] = topic
            item['url']=url
            logging.info(post_msg)
            items.append(item)
        return items

    def parseText(self, str):
        soup = BeautifulSoup(str, 'html.parser')
        return re.sub(" +|\n|\r|\t|\0|\x0b|\xa0",' ',soup.get_text()).strip()
