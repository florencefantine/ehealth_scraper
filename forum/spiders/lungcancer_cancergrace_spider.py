import scrapy
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.selector import Selector
from forum.items import PostItemsList
import re
import logging

# Spider for crawling Adidas website for shoes
class ForumsSpider(CrawlSpider):
    name = "lungcancer_cancergrace_spider"
    allowed_domains = ["cancergrace.org"]
    start_urls = [
        "http://cancergrace.org/forum/lung-thoracic-cancer/general-lung-thoracic-cancer",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                    restrict_xpaths='//td[@class="bbp-topic-title"]/a',
                ), callback='parsePostsList'),
            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                    restrict_xpaths='//div[@class="bbp-pagination-links"]/a[@class="next page-numbers"]'
                ), follow=True),
        )

    # https://github.com/scrapy/dirbot/blob/master/dirbot/spiders/dmoz.py
    # https://github.com/scrapy/dirbot/blob/master/dirbot/pipelines.py
    def parsePostsList(self,response):
        sel = Selector(response)
        posts = sel.xpath('//tr[contains(@id,"post")]')
        dates = sel.xpath('//tr[@class="bbp-reply-header"]')
        condition = 'lung cancer'
        items = []
        topic = response.xpath('//h2[@class="grace-postheader"]/text()').extract_first().strip()
        url = response.url

        for post, date in zip(posts,dates):
            item = PostItemsList()
            item['author'] = post.xpath('./td[@class="bbp-reply-author"]/a[2]/text()').extract_first()
            item['author_link'] = post.xpath('./td[@class="bbp-reply-author"]/a[2]/@href').extract_first()
            item['create_date'] = date.xpath('./td/text()').extract_first().strip()
            item['post'] = re.sub('\s+',' '," ".join(post.xpath('./td[@class="bbp-reply-content"]/p/text()').extract()).replace("\t","").replace("\n","").replace("\r",""))
            item['tag']=''
            item['topic'] = topic
            item['url']=url
            logging.info(item.__str__)
            items.append(item)
        return items
