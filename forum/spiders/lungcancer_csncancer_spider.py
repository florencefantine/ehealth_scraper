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

# Spider for crawling Adidas website for shoes
class ForumsSpider(CrawlSpider):
    name = "lungcancer_cancer_spider"
    allowed_domains = ["csn.cancer.org"]
    start_urls = [
        "https://csn.cancer.org/forum/129",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                    restrict_xpaths='//td[@class="title"]/a',
                ), callback='parsePostsList'),
            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                    restrict_xpaths='//a[@title="Go to next page"]'
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
        posts = sel.xpath('//div[@id="comments"]/table')
        items = []
        condition="lung cancer"
        topic = response.xpath('//div[@class="left-corner"]/h2/text()').extract_first()
        url = response.url

        item = PostItemsList()
        item['author'] = response.xpath('.//table[@class="node node-forum"]//div[@class="author"]/text()').extract_first()
        item['author_link'] = ''
        item['condition'] = condition
        create_date = response.xpath('.//table[@class="node node-forum"]//div[@class="date"]/span/text()').extract_first()
        item['create_date'] = self.getDate(create_date)
        item['post'] = re.sub('\s+',' '," ".join(response.xpath('.//table[@class="node node-forum"]//div[@class="content"]/p/text()').extract()).replace("\t","").replace("\n","").replace("\r","").replace(u'\xa0',''))
        item['tag']=''
        item['topic'] = topic
        item['url']=url
        items.append(item)
        
        for post in posts:
            item = PostItemsList()
            item['author'] = post.xpath('.//div[@class="author"]/text()').extract_first()
            item['author_link'] = ''
            item['condition'] = condition
            item['create_date'] = self.getDate(post.xpath('.//div[@class="date"]/span/text()').extract_first())
            item['post'] = self.cleanText(" ".join(post.xpath('.//div[@class="content"]/p/text()').extract()))
            # item['tag']='epilepsy'
            item['topic'] = topic
            item['url']=url
            items.append(item)
        return items
