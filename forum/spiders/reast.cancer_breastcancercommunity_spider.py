# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from forum.items import PostItemsList


class EpilepsyBreastcancerSpiderSpider(CrawlSpider):
    name = 'breast.cancer_breastcancercommunity_spider'
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

        url = response.url
        subject = response.xpath(
            '//p[@id="crumbs"]/a[2]/text()').extract()[0].strip()
        original_author = response.xpath(
            '//div[@class="original-topic"]//div[@class="user-post"]/p/strong/a/text()').extract()[0]
        original_author_link = response.xpath(
            '//div[@class="original-topic"]//div[@class="user-post"]/p/strong/a/@href').extract()[0]
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
        item['create_date'] = original_create_date
        item['post'] = original_message
        item['tag'] = 'epilepsy'
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


            item['author'] = author
            item['author_link'] = author_link
            item['create_date'] = create_date
            item['post'] = message
            item['tag'] = 'epilepsy'
            item['topic'] = subject
            item['url'] = url
            items.append(item)

        return items