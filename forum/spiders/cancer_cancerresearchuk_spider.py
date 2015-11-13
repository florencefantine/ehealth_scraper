import scrapy
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.selector import Selector
from forum.items import PostItemsList
import re
import logging

# Spider for crawling Adidas website for shoes
class ForumsSpider(CrawlSpider):
    name = "cancer_cancerresearchuk_spider"
    allowed_domains = ["www.cancerresearchuk.org"]
    start_urls = [
        "https://www.cancerresearchuk.org/about-cancer/cancer-chat/",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                    restrict_xpaths='//div[@class="tl-cell views-field views-field-nothing"]/a',
                ), callback='parsePostsList'),
            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                    restrict_xpaths='//a[@title="Go to next page"]'
                ), follow=True),
        )

    # https://github.com/scrapy/dirbot/blob/master/dirbot/spiders/dmoz.py
    # https://github.com/scrapy/dirbot/blob/master/dirbot/pipelines.py
    def parsePostsList(self,response):
        sel = Selector(response)
        posts = sel.xpath('//div[@class="view-content"]/div[contains(@class, "views-row")]/div[contains(@id, "post")]')
        items = []
        topic = response.xpath('//h1[@class="page-header"]/text()').extract_first()
        url = response.url
        
        for post in posts:
            item = PostItemsList()
            item['author'] = post.xpath('.//a[@class="username"]/text()').extract_first()
            item['author_link'] = post.xpath('.//a[@class="username"]/@href').extract_first()
            item['condition'] = "cancer"
            item['create_date'] = post.xpath('.//span[@class="post-created hidden-xs"]/text()').extract_first()
            if not item['create_date']:
                item['create_date'] = post.xpath('.//span[@class="post-is-reply-to"]/text()').extract_first().replace('in response to','').strip()

            item['post'] = re.sub('\s+',' '," ".join(post.xpath('.//div[@class="field-item even"]/p/text()').extract()).replace("\t","").replace("\n","").replace("\r","").replace(u'\xa0',''))
            item['tag']=''
            item['topic'] = topic
            item['url']=url
            logging.info(item.__str__)
            items.append(item)
        return items
