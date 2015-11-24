# -*- coding: utf-8 -*-
# import scrapy
import hashlib
# from scrapy.http import Request
# from bs4 import BeautifulSoup
# from forum.items import PostItemsList
# import logging
# import re

# class Health1Spider(scrapy.Spider):
#     name = "breastcancer_inspire_spider"
#     allowed_domains = ["inspire.com"]
#     start_urls = (
#         'https://www.inspire.com/signin.pl/',
#     )

#     def parse(self, response):
#         return [scrapy.FormRequest.from_response(response,formdata={"email":"pip99tom@yahoo.com",
#                     'pw':"aleluya11"},
#                      callback=self.after_login)]                   

#     def after_login(self,response):
#         urls = ['https://www.inspire.com/groups/advanced-breast-cancer/new/active/?page=%s' % page for page in xrange(1,594)]
#         for link in urls:
#             yield Request(link,callback=self.parse_list)

#     def parse_list(self,response):
#         links = response.xpath("id('search-results')/h3/a/@href").extract()
#         for link in links:
#             yield Request(link,callback=self.parse_posts)

#     def parse_posts(self, response):
        
#         """from scrapy.shell import inspect_response
#         inspect_response(response, self)"""
#         soup = BeautifulSoup(response.body)
#         posts = soup.find('div',{'class':'content-primary-post'})
#         posts = [x for x in posts.findAll('ul')]
#         posteos = []
#         for post in posts:
#             if re.findall('By.*', post.li.text) != []:
#         posteos.append( re.findall('By.*', post.li.text))
#     principal = soup.find('div',{'class':'post-body'}).text.replace("\n"," ").replace("\r"," ")
#     secundarios = [com.p for com in soup.findAll('div',{'id':re.compile('cmnt.*')})]
#     totales = []
#     totales.append(principal)
#     for x in secundarios:
#             totales.append(x.text.replace("\n"," ").replace("\r"," "))
#         items = []
#         date =[]
#         dates =  soup.findAll('li',{'class':'by'})
#         for d in dates:
#             if re.findall('\w* \d.*, \d*',d.text) != []:
#         date.append(re.findall('\w* \d.*, \d*', d.text))
#     authors = []
#     href = [x.find('a')['href'] for x in soup.findAll('li',{'class':'by'}) if x.find('a') is not None]
#     for x in href:
#             if "member" in x:
#         authors.append(x)
#         topic = soup.find('h1').text
#         url = response.url
#         condition = "breast cancer"
#         for x in range(len(posteos)):
#             item=PostItemsList()
#             item['author'] = posteos[x][0]
#             item['author_link']=authors[x]
#             item['create_date']= date[x][0]
#             item['post'] = totales[x]
#             item['tag']=''
#             item['topic'] = topic
#             item['url']=url
#             logging.info(item.__str__)
#             items.append(item)
#         return items   

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

class ForumsSpider(CrawlSpider):
    name = "breastcancer_inspire_spider"
    allowed_domains = ["inspire.com"]
    start_urls = [
        "https://www.inspire.com/groups/advanced-breast-cancer/",
    ]

    rules = (
            Rule(LinkExtractor(
                restrict_xpaths='//*[@id="search-results"]/h3',
                canonicalize=True,
                ), callback='parsePost', follow=True),
            Rule(LinkExtractor(
                restrict_xpaths='//div[contains(@class, "pagination-home")]',
                canonicalize=True,
            ), follow=True),
            Rule(LinkExtractor(
                restrict_xpaths='//div[contains(@class, "pagination")]',
                canonicalize=True,
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
            
    def parsePost(self,response):
        logging.info(response)
        sel = Selector(response)
        condition="breast cancer"
        posts = sel.css('.comments-box')
        items = []
        topic = sel.css('.post-title').xpath('./text()').extract()[0].strip()
        url = response.url

        item = PostItemsList()
        item['author'] = self.parseText(str=sel.css('.content-primary-post').xpath('./div[1]/ul/li[1]/a').extract()[0].strip())
        item['author_link']=response.urljoin(sel.css('.content-primary-post').xpath('./div[1]/ul/li[1]/a/@href').extract()[0])
        item['condition']=condition
        create_date = self.parseText(sel.css('.content-primary-post').xpath('./div[1]/ul/li[1]/text()').extract()[1].split('\n')[1].strip()[1:])
        item['create_date'] = self.getDate(create_date)
        item['domain'] = "".join(self.allowed_domains)
        post_msg=self.parseText(str=sel.css('.content-primary-post').xpath('./div[2]/p').extract()[0])
        item['post']=post_msg
        # item['tag']=''
        item['topic'] = topic
        item['url']=url
        logging.info(post_msg)
        items.append(item)
        for post in posts:
            if len(post.css('.post-info'))==0:
                continue
            item = PostItemsList()
            item['author'] = self.parseText(str=post.css('.post-info').xpath('./ul/li[1]/a').extract()[0].strip())
            item['author_link']=response.urljoin(post.css('.post-info').xpath('./ul/li[1]/a/@href').extract()[0])
            item['condition']=condition
            item['create_date'] = self.parseText(str=post.css('.post-info').xpath('./ul/li[3]').extract()[0])
            item['domain'] = "".join(self.allowed_domains)
            post_msg=self.parseText(str=post.xpath('./p').extract()[0])
            item['post']=post_msg
            # item['tag']=''
            item['topic'] = topic
            item['url']=url
            logging.info(post_msg)
            items.append(item)
        return items

    def parseText(self, str):
        soup = BeautifulSoup(str, 'html.parser')
        return re.sub(" +|\n|\r|\t|\0|\x0b|\xa0",' ',soup.get_text()).strip()
