import scrapy
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.selector import Selector
from forum.items import PostItemsList
import re
import logging

# Spider for crawling Adidas website for shoes
class ForumsSpider(CrawlSpider):
    name = "lymphoma_inspire_spider"
    allowed_domains = ["www.inspire.com"]
    start_urls = [
        "https://www.inspire.com/groups/leukemia-lymphoma-and-myeloma/discussions/",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                    restrict_xpaths='//div[@id="search-results"]/h3/a',
                ), callback='parsePostsList'),
            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                    restrict_xpaths='//ul[@class="search-results-nav"]/li[last()-1]/a'
                ), follow=True),
        )

    # https://github.com/scrapy/dirbot/blob/master/dirbot/spiders/dmoz.py
    # https://github.com/scrapy/dirbot/blob/master/dirbot/pipelines.py
    def parsePostsList(self,response):
        sel = Selector(response)
        posts = sel.xpath('//div[@class="content-primary-post"]/div[@class="comments-box"]')
        items = []
        condition="lymphoma"
        topic = response.xpath('//h1[@class="post-title"]/text()').extract_first()
        url = response.url
        
        item = PostItemsList()
        item['author'] = response.xpath('//div[@class="content-primary-post"]/div[@class="post-info"]//li[@class="by"]/a/text()').extract_first()
        item['author_link'] = response.xpath('//div[@class="content-primary-post"]/div[@class="post-info"]//li[@class="by"]/a/@href').extract_first()

        item['create_date'] = response.xpath('//div[@class="content-primary-post"]/div[@class="post-info"]//li[@class="by"]/text()').extract()[1].strip().split(' ')
        item['condition'] = condition
        item['create_date'] = ' '. join(item['create_date'][1:-2])[:-2]
        item['post'] = re.sub('\s+',' '," ".join(response.xpath('//div[@class="content-primary-post"]/div[@class="post-body"]/p/text()').extract()).replace("\t","").replace("\n","").replace("\r",""))
        item['tag']=''
        item['topic'] = topic
        item['url']=url
        logging.info(item.__str__)
        items.append(item)
        
        for post in posts:
            item = PostItemsList()
            item['author'] = post.xpath('./div[@class="post-info"]//li[@class="by"][1]/a/text()').extract_first()
            if item['author']:
                item['author_link'] = post.xpath('./div[@class="post-info"]//li[@class="by"][1]/a/@href').extract_first()
                item['condition'] = condition
                item['create_date'] = post.xpath('./div[@class="post-info"]//li[@class="by"][3]/text()').extract_first()
                item['post'] = re.sub('\s+',' '," ".join(post.xpath('./p/text()').extract()).replace("\t","").replace("\n","").replace("\r",""))
                item['tag']=''
                item['topic'] = topic
                item['url']=url
                logging.info(item.__str__)
                items.append(item)
        return items
