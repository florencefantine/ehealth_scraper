# -*- coding: utf-8 -*-
# import scrapy
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
    name = "all_inspire_spider"
    allowed_domains = ["inspire.com"]
    start_urls = [
        "https://www.inspire.com/groups/advanced-breast-cancer/",
        "https://www.inspire.com/groups/american-lung-association-lung-cancer-survivors/",
        "https://www.inspire.com/groups/leukemia-lymphoma-and-myeloma/",
        "https://www.inspire.com/groups/hepatitis-c/",
        "https://www.inspire.com/groups/hiv-and-aids/",
        "https://www.inspire.com/groups/leukemia-lymphoma-and-myeloma/discussions/",
        "https://www.inspire.com/search/?query=multiple+sclerosis",
        "https://www.inspire.com/groups/kidney-cancer-association/",
        "https://www.inspire.com/search/?query=rheumatoid+arthritis"
    ]

    rules = (
            Rule(LinkExtractor(
                restrict_xpaths='//h3/a',
                canonicalize=True,
                ), callback='parsePost', follow=True),
            Rule(LinkExtractor(
                restrict_xpaths='//ul[@class="pagination"]',
                canonicalize=True,
            ), follow=True),
        )

    def getDate(self,date_str):
        # date_str="Fri Feb 12, 2010 1:54 pm"
        try:
            date = dateparser.parse(date_str)
            epoch = int(date.strftime('%s'))
            create_date = time.strftime("%Y-%m-%d'T'%H:%M%S%z",  time.gmtime(epoch))
            return str(epoch)
        except Exception:
            #logging.error(">>>>>"+date_str)
            return date_str

    def addUUID(self,item):
        newStr = None
        try:
            newStr = item['author']+item['author_link']+item['create_date']+item['post']+item['topic']+item['url']+item['condition']
        except Exception:
            return None
        return newStr

    def parsePost(self,response):
        logging.info(response)
        sel = Selector(response)
        posts = sel.xpath('//article[@class="post"]')
        items = []
        topic = ''.join(sel.xpath('//header[@class="header-post"]/h4/a/text()').extract())
        condition = topic
        url = response.url

        for post in posts:
            item = PostItemsList()
            item['author'] = ''.join(post.xpath('.//div[@class="username"]/a/text()').extract())
            item['author_link']= response.urljoin(''.join(post.xpath('.//div[@class="username"]/a/@href').extract()) )
            item['condition']= condition
            item['create_date'] = self.getDate(''.join(post.xpath('.//time/@datetime').extract()))
            post_msg= ''.join(post.xpath('.//div[@class="post-content"]//text()').extract())
            item['post']= self.parseText(post_msg)
            # item['tag']=''
            item['topic'] = topic
            item['url']=url
            logging.info(post_msg)
            items.append(item)
            uuid = self.addUUID(item)
            if not uuid is None:
                try:
                    item['post_id']= hashlib.md5(uuid).hexdigest()[:9]
                    items.append(item)
                except Exception:
                    logging.error("not able to hash "+uuid)
        return items

    def parseText(self, str):
        soup = BeautifulSoup(str, 'html.parser')
        return re.sub(" +|\n|\r|\t|\0|\x0b|\xa0",' ',soup.get_text()).strip()
