# -*- coding: utf-8 -*-
import scrapy
import hashlib
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from bs4 import BeautifulSoup
from forum.items import PostItemsList
import re
# from helpers import cleanText
import string
import dateparser
import time

class EpilepsyBreastcancerSpiderSpider(CrawlSpider):
    name = 'breastcancer_community_spider'
    allowed_domains = ['breastcancer.org']
    start_urls = ['https://community.breastcancer.org/']

    rules = (
        Rule(LinkExtractor(allow=r'/forum/\d+$'), follow=True),
        Rule(LinkExtractor(allow=r'/forum/\d+/topics/\d+$'), follow=True),
        Rule(
            LinkExtractor(allow=(r'/forum/\d+/topics/\d+\?page=\d+')),
            callback='parse_item', follow=True),
        Rule(LinkExtractor(allow=r'/forum/\d+\?page=\d+$'), follow=True),
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

        def clean_date(date):
            if len(date) > 1:
                date = date[0].split('\n')
                date = date[2]
                return date.strip()
            else:
                date = date[0].split('\n')[2]
                return date.strip()
        condition="breast cancer"
        url = response.url
        subject = response.xpath(
            '//p[@id="crumbs"]/a[2]/text()').extract()[0].strip()
        original_author = response.xpath(
            '//div[@class="original-topic"]//div[@class="user-post"]/p/strong/a/text()')\
            .extract()[0]
        original_author_link = response.xpath(
            '//div[@class="original-topic"]//div[@class="user-post"]/p/strong/a/@href')\
            .extract()[0]
        original_create_date = response.xpath(
            '//div[@class="original-topic"]//span[@class="posted-time left"]//text()'
        ).extract()
        original_message = "".join(response.xpath(
            '//div[@class="original-topic"]//div[@class="user-post"]//text()'
        ).extract()).strip()
        posts = response.xpath(
            '//div[@class="post"]|//div[class="post secondary"]')

        item = PostItemsList()

        item['author'] = original_author
        item['author_link'] = original_author_link
        item['condition'] = condition
        item['create_date'] = self.getDate(original_create_date)
        item['post'] = self.cleanText(original_message)
        # item['tag'] = ''
        item['topic'] = subject
        item['url'] = url
        items.append(item)

        for post in posts:
            author = post.xpath(
                './/div[@class="user-info"]/a/text()').extract()[0]
            author_link = post.xpath(
                './/div[@class="user-info"]/a/@href').extract()[0]
            author_link = response.urljoin(author_link)
            create_date = post.xpath(
                './/p[@class="post-time"]/strong/text()').extract()[0]
            message = post.xpath(
                './/div[@class="user-post"]//p[not(@class="post-time")]//text()').extract()
            message = "".join(message).strip()
            message = self.cleanText(message)

            item['author'] = author
            item['author_link'] = author_link
            item['condition'] = condition
            item['create_date'] = self.getDate(create_date)
            item['post'] = self.cleanText(message)
            # item['tag'] = ''
            item['topic'] = subject
            item['url'] = url
            items.append(item)

        return items
