import scrapy
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.selector import Selector
from forum.items import PostItemsList
import re
import logging

# from helpers import cleanText


class ForumsSpider(CrawlSpider):
    name = "multiplesclerosis_medhelp_spider"
    allowed_domains = ["medhelp.org"]
    start_urls = [
        "http://www.medhelp.org/forums/Multiple-Sclerosis/show/41",
    ]

    rules = (
        Rule(LinkExtractor(
            restrict_xpaths='//div[@class="fonts_resizable_subject subject_title "]',
        ), callback="parsePostsList", follow=True),

        Rule(LinkExtractor(
            allow=(r"\?page=\d+"),
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
        posts = response.xpath('//div[@class="post_data has_bg_color"]')[1:]
        subject = response.url.split("/")[5].replace("-", " ")
        condiiton="multiple sclerosis"

        for post in posts:
            item = PostItemsList()
            author = post.xpath(
                './/a[contains(@id, "user_")]/text()').extract()[0]
            author_link = post.xpath(
                './/a[contains(@id, "user_")]/@href').extract()[0]
            author_link = response.urljoin(author_link)
            create_date = post.xpath(
                './/div[@class="user_info user_info_comment"]/div[@class="float_fix"]//text()')\
                .extract()[-2].strip()
            message = " ".join(post.xpath(
                './/div[@class="KonaBody"]//text()').extract())
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
