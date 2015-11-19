from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from forum.items import PostItemsList
import re
from bs4 import BeautifulSoup

# import lxml.html
# from lxml.etree import ParserError
# from lxml.cssselect import CSSSelector

# LOGGING to file
# import logging
# from scrapy.log import ScrapyFileLogObserver

# logfile = open('testlog.log', 'w')
# log_observer = ScrapyFileLogObserver(logfile, level=logging.DEBUG)
# log_observer.start()

# Spider for crawling Adidas website for shoes


class ForumsSpider(CrawlSpider):
    name = "lymphoma_macmillan_spider"
    allowed_domains = ["macmillan.org.uk"]
    start_urls = [
        "https://community.macmillan.org.uk/cancer_types/non-hodgkin-lymphoma/discussions",
    ]

    rules = (
        Rule(LinkExtractor(
            restrict_xpaths='//div[@class="pager ui-page"]',canonicalize=True),
            follow=True, callback='topic_parse'),
        Rule(LinkExtractor(
            restrict_xpaths='//h4[@class="post-name"]',canonicalize=True),
            follow=True, callback='topic_parse'),
    )

    def cleanText(self,text):
        soup = BeautifulSoup(text,'html.parser')
        text = soup.get_text();
        text = re.sub("( +|\n|\r|\t|\0|\x0b|\xa0|\xbb|\xab)+",' ',text).strip()
        return text 

    def topic_parse(self, response):
        if 'discussions' not in response.url:
            items = []
            condition = "Lymphoma"
            subject = response.xpath(
                '//div[@class="forum-stats-container"]/h1/text()').extract()[0]
            subject = subject.strip()
            url = response.url
            posts = response.xpath(
                '//div[@class="full-post-container fiji-full-post-container evolution2-full-post-container"]')

            for post in posts:
                item = PostItemsList()
                author = post.xpath(
                    './/span[@class="user-name"]/a/text()')\
                    .extract()[1].strip()
                author_link = post.xpath(
                    './/span[@class="user-name"]/a/@href').extract()[0]
                create_date = post.xpath(
                    './/a[@class="internal-link view-post"]/text()')\
                    .extract()[0]
                message = ' '.join(post.xpath(
                    './/div[@class="post-content user-defined-markup"]//text()'
                ).extract())
                message = self.cleanText(message)

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
