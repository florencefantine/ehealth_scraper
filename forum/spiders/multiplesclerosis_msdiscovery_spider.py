import scrapy
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.selector import Selector
from forum.items import PostItemsList
import re
import logging

# from helpers import cleanText


class ForumsSpider(CrawlSpider):
    name = "multiplesclerosis_msdiscovery_spider"
    allowed_domains = ["www.msdiscovery.org"]
    start_urls = [
        "http://www.msdiscovery.org/forums/discussion",
    ]

    rules = (
        Rule(LinkExtractor(
            allow=(r"http://www\.msdiscovery\.org/forums/discussion/"),
        ), callback="parsePostsList", follow=True),

        Rule(LinkExtractor(
            allow=r"sort_by=created&sort_order=DESC&page=\d+",
        ), follow=True),

    )
    def cleanText(self,text):
        soup = BeautifulSoup(text,'html.parser')
        text = soup.get_text();
        text = re.sub("( +|\n|\r|\t|\0|\x0b|\xa0|\xbb|\xab)+",' ',text).strip()
        return text 


    def parsePostsList(self, response):
        items = []

        url = response.url
        subject = response.xpath(
            '//h1[@class="node-title"]/text()').extract()[0]
        original_author = response.xpath(
            '//div[@class="node-byline"]/text()').extract()[0]
        original_author_link = "no"
        original_create_date = response.xpath(
            '//span[@class="node-date"]/span/text()').extract()[0]
        original_message = " ".join(response.xpath(
            '//div[@class="field-item even"]//text()').extract())
        original_message = self.cleanText(original_message)
        condiiton="multiple sclerosis"

        item = PostItemsList()
        item['author'] = original_author
        item['author_link'] = original_author_link
        item['condition'] = condition
        item['create_date'] = original_create_date
        item['post'] = original_message
        item['tag'] = 'epilepsy'
        item['topic'] = subject
        item['url'] = url

        items.append(item)

        posts = response.xpath('//article[contains(@class, "comment")]')
        for post in posts:
            author = post.xpath(
                './/div[@class="node-author"]/span/text()').extract()[0]
            author_link = "no"
            create_date = post.xpath(
                './/div[@class="node-date"]/time/text()').extract()[0]
            message = " ".join(post.xpath(
                './/div[@class="field-item even"]//text()').extract())
            message = cleanText(message)

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
