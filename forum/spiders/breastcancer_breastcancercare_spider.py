# -*- coding: utf-8 -*-
from scrapy.linkextractors import LinkExtractor
import hashlib
from scrapy.spiders import CrawlSpider, Rule
from bs4 import BeautifulSoup
import re
from forum.items import PostItemsList
import string
import dateparser
import time


class EpilepsyBreastcancercareSpiderSpider(CrawlSpider):
    name = 'breastcancer_breastcancercare_spider'
    allowed_domains = ['breastcancercare.org.uk']
    start_urls = ['https://forum.breastcancercare.org.uk/']

    rules = (
        Rule(LinkExtractor(
            # all forums
            restrict_xpaths='//div[contains(@class, "categories-rows")]',canonicalize=True),
            follow=True, callback='parse_item'),

        Rule(LinkExtractor(
            # all topics
            restrict_xpaths='//div[@class="board-title"]',canonicalize=True),
            follow=True),


        Rule(LinkExtractor(
            # all threads
            restrict_xpaths='//h2[@class="message-subject"]',canonicalize=True),
            callback='parse_item', follow=True),

        Rule(LinkExtractor(
            # next page for all threads list
            restrict_xpaths='//a[@rel="next"]',canonicalize=True),
            follow=True),

        Rule(LinkExtractor(
            # next page for thread
            restrict_xpaths='//li[@class="lia-paging-page-next lia-component-next"]',canonicalize=True),
            follow=True),
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
            ##logging.error(">>>>>"+date_str)
            return date_str
            
    def parse_item(self, response):

        def clean_date(date, time):
            '''helper method for clean date'''
            date = date.replace(u'\u200e', '')
            return u' '.join([date, time])

        items = []
        condition="breast cancer"
        url = response.url
        subject = response.xpath(
            '//span[@class="lia-link-navigation child-thread lia-link-disabled"]//text()').extract()
        subject = ''.join([item.strip() for item in subject])
        posts = response.xpath(
            '//div[@class="lia-linear-display-message-view"]')
        for post in posts:
            item = PostItemsList()
            author = post.xpath(
                './/a[contains(@class, "lia-user-name-link")]//text()')\
                .extract()[0]
            author_link = post.xpath(
                './/a[contains(@class, "lia-user-name-link")]/@href')\
                .extract()[0]
            author_link = response.urljoin(author_link)
            create_date = post.xpath(
                './/span[@class="local-date"]/text()').extract()[1]
            create_time = post.xpath(
                './/span[@class="local-time"]//text()').extract()[0]
            create_date = clean_date(create_date, create_time)

            message = ''.join(post.xpath(
                './/div[@class="lia-message-body-content"]//text()')
                .extract())
            # message = self.cleanText(message)

            item['author'] = author
            item['author_link'] = author_link
            item['condition'] = condition
            item['create_date'] = self.getDate(create_date)
            item['post'] = self.cleanText(message)
            # item['tag'] = 'epilepsy'
            item['topic'] = subject
            item['url'] = url

            items.append(item)
        return items
