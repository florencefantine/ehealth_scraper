import scrapy
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.selector import Selector
from forum.items import PostItemsList
import re
import logging

# from helpers import cleanText


class ForumsSpider(CrawlSpider):
    name = "multiplesclerosis_msworld_spider"
    allowed_domains = ["msworld.org"]
    start_urls = [
        "http://www.msworld.org/forum/",
    ]


    rules = (
        Rule(LinkExtractor(
            restrict_xpaths='//h2[@class="forumtitle"]',
        ), callback="replace_link", follow=True),

        Rule(LinkExtractor(
            allow=(r"forumdisplay\.php\?.+/page\d+")
        ), callback="replace_link", follow=True),

        Rule(LinkExtractor(
            allow=(r"showthread.php")
        ), callback="parsePostsList", follow=True),
    )

    def cleanText(self,text):
        soup = BeautifulSoup(text,'html.parser')
        text = soup.get_text();
        text = re.sub("( +|\n|\r|\t|\0|\x0b|\xa0|\xbb|\xab)+",' ',text).strip()
        return text 


    def replace_link(self, response):
        # little hack for remove request string from url
        url = response.url.split("=&")[0]
        yield scrapy.Request(url, self.parsePostsList)

    def parsePostsList(self, response):
        items = []
        url = response.url
        condiiton="multiple sclerosis"
        subject = response.xpath(
            '//li[@class="navbit lastnavbit"]/span/text()').extract()
        posts = response.xpath(
            '//li[@class="postbit postbitim postcontainer old"]')
        for post in posts:
            item = PostItemsList()
            author = post.xpath(
                './/a[contains(@class, "username")]/strong/text()')\
                .extract()[0]
            author_link = post.xpath(
                './/a[contains(@class, "username")]/@href').extract()[0]
            author_link = response.urljoin(author_link)
            create_date = " ".join(post.xpath(
                './/span[@class="date"]//text()').extract())
            message = " ".join(post.xpath(
                './/div[contains(@id, "post_message_")]//text()').extract())
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
