# -*- coding: utf-8 -*-
import scrapy
import hashlib
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

# Spider for crawling Adidas website for shoes
class ForumsSpider(CrawlSpider):
    name = "cancer_cancerresearchuk_spider"
    allowed_domains = ["www.cancerresearchuk.org"]
    start_urls = [
        "https://www.cancerresearchuk.org/about-cancer/cancer-chat/",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                restrict_xpaths='//div[@class="tl-cell views-field views-field-nothing"]/a'
                ,canonicalize=True
                ), callback='parsePostsList'),
            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                restrict_xpaths='//a[@title="Go to next page"]'
                ,canonicalize=True
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
    def parsePostsList(self,response):
        sel = Selector(response)
        posts = sel.xpath('//div[@class="view-content"]/div[contains(@class, "views-row")]/div[contains(@id, "post")]')
        items = []
        topic = response.xpath('//h1[@class="page-header"]/text()').extract_first()
        url = response.url
        
        for post in posts:
            item = PostItemsList()
            item['author'] = post.xpath('.//a[@class="username"]/text()').extract_first()
            item['author_link'] = post.xpath('.//a[@class="username"]/@href').extract_first()
            item['condition'] = "cancer"
            item['create_date'] = self.getDate(post.xpath('.//span[@class="post-created hidden-xs"]/text()').extract_first())
            if not item['create_date']:
                item['create_date'] = self.getDate(post.xpath('.//span[@class="post-is-reply-to"]/text()').extract_first().replace('in response to','').strip())
            item['domain'] = "".join(self.allowed_domains)
            item['post'] = re.sub('\s+',' '," ".join(post.xpath('.//div[@class="field-item even"]/p/text()').extract()).replace("\t","").replace("\n","").replace("\r","").replace(u'\xa0',''))
            # item['tag']=''
            item['topic'] = topic
            item['url']=url
            logging.info(item.__str__)
            items.append(item)
        return items


# import scrapy
# from scrapy.contrib.spiders import CrawlSpider, Rule
# from scrapy.contrib.linkextractors import LinkExtractor
# from scrapy.selector import Selector
# from forum.items import PostItemsList
# import re
# import logging
# from bs4 import BeautifulSoup
# class ForumsSpider(CrawlSpider):
#     name = "breastcancer_cancerresearchuk_spider"
#     allowed_domains = ["cancerresearchuk.org"]
#     start_urls = [
#         "https://www.cancerresearchuk.org/about-cancer/cancer-chat/",
#     ]

#     rules = (
#             Rule(LinkExtractor(
#                     restrict_xpaths='//div[contains(@class,"table-list views-table cols-5")]/ol/li/div[1]/a[1]',
#                 ), callback='parsePostsList'),
#             Rule(LinkExtractor(
#                     restrict_xpaths='//li[@class="next last"]',
#                 ), follow=True),
#         )
#     def parsePostsList(self,response):
#         sel = Selector(response)
#         html = response.body
#         soup = BeautifulSoup(html)
#         users = soup.findAll('a',{'class':'username'})
#         items = []
#         topic = response.xpath('//h1/text()').extract()
#         url = response.url
#         for x in range(len(users)):
#             item = PostItemsList()
#             item['author'] = soup.findAll('a',{'class':'username'})[x].text
#             item['author_link']=soup.findAll('a',{'class':'username'})[x]['href']
#             item['create_date']= soup.findAll('div',{'class':'post-content-inner'})[x].span.text[0:11]
#             item['post'] = soup.findAll('div',{'class':'post-content-inner'})[x].find('div',{'class':'field-item even'}).text
#             item['tag']='cancer'
#             item['topic'] = topic
#             item['url']=url
#             logging.info(item.__str__)
#             items.append(item)
#         return items
