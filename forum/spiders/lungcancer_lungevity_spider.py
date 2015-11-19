import scrapy
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.selector import Selector
from forum.items import PostItemsList
import re
import logging

# Spider for crawling Adidas website for shoes
class ForumsSpider(CrawlSpider):
    name = "lungcancer_lungevity_spider"
    allowed_domains = ["lungevity.org"]
    start_urls = [
        "http://forums.lungevity.org/index.php?/forum/19-general/",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                    restrict_xpaths='//a[@class="expander closed"]',
                ), callback='parsePostsList'),
            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                    restrict_xpaths='//li[@class="next"]/a[@rel="next"]'
                ), follow=True),
        )

    # https://github.com/scrapy/dirbot/blob/master/dirbot/spiders/dmoz.py
    # https://github.com/scrapy/dirbot/blob/master/dirbot/pipelines.py
    def parsePostsList(self,response):
        sel = Selector(response)
        posts = sel.css('.post_wrap')
        items = []
        topic = response.xpath('//h1[@class="ipsType_pagetitle"]/text()').extract_first()
        url = response.url
        
        condition="lung cancer"
        for post in posts:
            item = PostItemsList()
            item['author'] = post.xpath('.//span[@class="author vcard"]/text()').extract_first()
            item['author_link'] = ''
            item['condition'] = condition
            item['create_date'] = post.xpath('.//abbr[@class="published" and itemprop="commentTime"]/text()').extract_first()
      
            item['post'] = re.sub('\s+',' '," ".join(post.xpath('.//div[@class="post entry-content " and itemprop="commentText"]/p/text()').extract()).replace("\t","").replace("\n","").replace("\r","").replace(u'\xa0',''))
            item['tag']=''
            item['topic'] = topic
            item['url']=url
            logging.info(item.__str__)
            items.append(item)
        return items
