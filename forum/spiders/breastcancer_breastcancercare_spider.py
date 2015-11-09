# -*- coding: utf-8 -*-
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from bs4 import BeautifulSoup
import re
from forum.items import PostItemsList


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

    def cleanText(self,text):
        soup = BeautifulSoup(text,'html.parser')
        text = soup.get_text();
        text = re.sub("( +|\n|\r|\t|\0|\x0b|\xa0|\xbb|\xab)+",' ',text).strip()
        return text 

    def parse_item(self, response):

        def clean_date(date, time):
            '''helper method for clean date'''
            date = date.replace(u'\u200e', '')
            return u' '.join([date, time])

        items = []
        condition="breast cancer"
        url = response.url
        subject = response.xpath(
            '//div[@class="lia-message-subject"]//text()').extract()
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
            message = self.cleanText(message)

            item['author'] = author
            item['author_link'] = author_link
            item['condition'] = condition
            item['create_date'] = create_date
            item['post'] = message
            item['tag'] = 'epilepsy'
            item['topic'] = subject
            item['url'] = url

            items.append(item)
        return items
