# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import re
from bs4 import BeautifulSoup
from forum.items import PostItemsList
import string
import dateparser
import time

class EpilepsyCancerSpiderSpider(CrawlSpider):
    name = 'breastcancer_cancerorg_spider'
    allowed_domains = ['csn.cancer.org']
    start_urls = ['https://csn.cancer.org/forum/127']

    rules = (
        Rule(LinkExtractor(
            restrict_xpaths='//td[@class="title"]'
            ,canonicalize=True),
            callback='parse_item', follow=True),

        # pagination
        Rule(LinkExtractor(allow=(r'/forum/127\?page=\d+'),canonicalize=True),
             follow=True),
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
            
    def cleanText(self,text):
        soup = BeautifulSoup(text,'html.parser')
        text = soup.get_text();
        text = re.sub("( +|\n|\r|\t|\0|\x0b|\xa0|\xbb|\xab)+",' ',text).strip()
        return text 
    
    def parse_item(self, response):
        items = []
        node_item = PostItemsList()
        condition="breast cancer"
        subject = response.xpath(
            '//div[@class="left-corner"]/h2/text()'
        ).extract()[0]
        url = response.url
        node_post = response.xpath('//table[@class="node node-forum"]')
        node_author = node_post.xpath(
            './/div[@class="author"]/text()').extract()[0]
        node_time = u''.join(
            node_post.xpath('.//div[@class="date"]//text()').extract()).strip()
        node_message = u''.join(
            node_post.xpath(
                './/div[@class="content"]//text()').extract())
        node_message = self.cleanText(node_message)
        posts = response.xpath('//table[@class="comment comment-forum"]')

        node_item['author'] = node_author
        node_item['author_link'] = ''
        node_item['condition'] = condition
        node_item['create_date'] = self.getDate(node_time)
        node_item['post'] = node_message
        # node_item['tag'] = 'epilepsy'
        node_item['topic'] = subject
        node_item['url'] = url

        items.append(node_item)

        for post in posts:
            item = PostItemsList()
            author = post.xpath('.//div[@class="author"]/text()').extract()[0]
            date = post.xpath('.//div[@class="date"]//text()').extract()[0]
            message = u''.join(
                post.xpath('.//div[@class="content"]//text()')
                .extract()).strip()

            item['author'] = author
            item['author_link'] = '*'
            item['condition'] = condition
            item['create_date'] = self.getDate(date)
            item['post'] = self.cleanText(message)
            # item['tag'] = 'epilepsy'
            item['topic'] = subject
            item['url'] = url

            items.append(item)
        return items
