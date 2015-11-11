# -*- coding: utf-8 -*-
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import re
from bs4 import BeautifulSoup
from forum.items import PostItemsList


class EpilepsyCancercompassSpiderSpider(CrawlSpider):
    name = 'lymphoma_cancercompass_spider'
    allowed_domains = ['cancercompass.com']
    start_urls = [
        'http://www.cancercompass.com/message-board/cancers/lymphoma/1,0,119,57.htm',
        'http://www.cancercompass.com/message-board/cancers/lymphoma/non-hodgkins/1,0,119,57,58.htm']

    rules = (
        Rule(LinkExtractor(restrict_xpaths='//a[@class="subLink"]',canonicalize=True),
             callback='parse_item', follow=True),

        Rule(LinkExtractor(restrict_xpaths='//a[contains(text(), "Next")]',canonicalize=True),
             callback='parse_item', follow=True),
    )

    def cleanText(self,text):
        soup = BeautifulSoup(text,'html.parser')
        text = soup.get_text();
        text = re.sub("( +|\n|\r|\t|\0|\x0b|\xa0|\xbb|\xab)+",' ',text).strip()
        return text 
    
    def parse_item(self, response):
        items = []
        if 'all' in response.url:
            url = response.url
            condition="Lymphoma"
            subject = response.xpath(
                '//div[@class="contentText"]/h1/text()').extract()[0]
            posts = response.xpath('//div[@class="mbpost"]')
            for post in posts:
                item = PostItemsList()
                author = post.xpath(
                    './/p/a/*[2]/text()|.//div[@class="author"]/p/span/text()')\
                    .extract()[0]
                author_link = post.xpath('.//p/a/@href').extract()
                if author_link:
                    author_link = author_link[0]
                else:
                    author_link = 'anon'
                create_date = post.xpath(
                    './/div[@class="header"]/p//text()').extract()
                if len(create_date) > 2:
                    create_date = create_date[2].strip()
                    create_date = create_date[
                        create_date.find('on') + 2:].strip()
                else:
                    create_date = create_date[0]
                    create_date = create_date[
                        create_date.find('on') + 2:].strip()
                message = u''.join(post.xpath(
                    './/div[@class="msgContent"]//text()')
                    .extract()[0])
                message = self.cleanText(message)
                #message = message.strip()

                item['author'] = author
                item['author_link'] = author_link
                item['condition'] = condition
                item['create_date'] = create_date
                item['post'] = message
                item['tag'] = 'Lymphoma'
                item['topic'] = subject
                item['url'] = url
                items.append(item)
            return items
