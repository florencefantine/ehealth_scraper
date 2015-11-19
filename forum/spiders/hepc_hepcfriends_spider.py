import scrapy
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.selector import Selector
from forum.items import PostItemsList
import re
import logging

# Spider for crawling Adidas website for shoes
class ForumsSpider(CrawlSpider):
    name = "hepc_hepcfriends_spider"
    allowed_domains = ["hepcfriends.activeboard.com"]
    start_urls = [
        "http://hepcfriends.activeboard.com/f388110/on-treatment/",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                    restrict_xpaths='//a[@class="topictitle"]',
                ), callback='parsePostsList'),
            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                    restrict_xpaths='//a[@title="Next"]'
                ), follow=True),
        )

    # https://github.com/scrapy/dirbot/blob/master/dirbot/spiders/dmoz.py
    # https://github.com/scrapy/dirbot/blob/master/dirbot/pipelines.py
    def parsePostsList(self,response):
        sel = Selector(response)
        posts = sel.xpath('//table[@id="abPreviewTbl"]//tr[contains(@class, "tr")]')
        items = []
        topic = response.xpath('//div[@class="breadcrumb-widget widget gen"]/span[@class="nolinks"]/text()').extract_first()
        url = response.url
        condition="hep c"
        
        for post in posts:
            item = PostItemsList()
            item['author'] = post.xpath('.//td[contains(@class, "td-first")]/div[@class="comment-meta"]/a/text()').extract_first()
            if item['author']:
                item['author_link'] = post.xpath('.//td[contains(@class, "td-first")]/div[@class="comment-meta"]/a/@href').extract_first()
                item['condition'] = condition
                item['create_date'] = post.xpath('.//td[contains(@class, "td-first")]//time/text()').extract_first()
          
                item['post'] = re.sub('\s+',' '," ".join(post.xpath('.//div[@class="comment-body postbody"]/p/text()').extract()).replace("\t","").replace("\n","").replace("\r","").replace(u'\xa0',''))
                item['tag']=''
                item['topic'] = topic
                item['url']=url
                logging.info(item.__str__)
                items.append(item)
        return items
