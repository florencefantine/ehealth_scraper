import scrapy
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.selector import Selector
from forum.items import PostItemsList
import re
import logging

# Spider for crawling Adidas website for shoes
class ForumsSpider(CrawlSpider):
    name = "lungcancer_macmillan_spider"
    allowed_domains = ["community.macmillan.org.uk"]
    start_urls = [
        "https://community.macmillan.org.uk/cancer_types/lung-cancer/discussions",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                    restrict_xpaths='//h4[@class="post-name"]/a', canonicalize=False,
                ), callback='parsePostsList'),
            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                    restrict_xpaths='//a[@class="next"]'
                ), follow=True),
        )



    # https://github.com/scrapy/dirbot/blob/master/dirbot/spiders/dmoz.py
    # https://github.com/scrapy/dirbot/blob/master/dirbot/pipelines.py
    def parsePostsList(self,response):
        sel = Selector(response)
        posts = sel.xpath('//ul[@class="content-list"]/li')
        condition="lung cancer"
        items = []
        topic = response.xpath('//h1/text()').extract_first().strip()
        url = response.url
        
        for post in posts:
            item = PostItemsList()
            item['author'] = post.xpath('.//span[@class="user-name"]/a/text()').extract()[1].strip()
            item['author_link'] = post.xpath('.//span[@class="user-name"]/a/@href').extract_first()
            item['condition'] = condition
            item['create_date'] = post.xpath('.//div[@class="post-date"]/span[@class="value"]/a/text()').extract_first()
      
            item['post'] = re.sub('\s+',' '," ".join(post.xpath('.//div[@class="post-content user-defined-markup"]/p/text()').extract()).replace("\t","").replace("\n","").replace("\r","").replace(u'\xa0',''))
            item['tag']='epilepsy'
            item['topic'] = topic
            item['url']=url
            logging.info(item.__str__)
            items.append(item)
        return items
