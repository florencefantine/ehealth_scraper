import scrapy
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.selector import Selector
from forum.items import PostItemsList
import re
import logging

## LOGGING to file
#import logging
#from scrapy.log import ScrapyFileLogObserver

#logfile = open('testlog.log', 'w')
#log_observer = ScrapyFileLogObserver(logfile, level=logging.DEBUG)
#log_observer.start()

# Spider for crawling Adidas website for shoes
class ForumsSpider(CrawlSpider):
    name = "hiv_ehealthforums_spider"
    allowed_domains = ["ehealthforum.com"]
    start_urls = [
        "http://ehealthforum.com/health/hiv_symptoms.html",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                    restrict_xpaths='//a[@class="topictitle "]',
                ), callback='parsePostsList'),
            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                    restrict_xpaths='//li[@class="pagination_number"]',
                ), follow=True),
        )

    # https://github.com/scrapy/dirbot/blob/master/dirbot/spiders/dmoz.py
    # https://github.com/scrapy/dirbot/blob/master/dirbot/pipelines.py
    def parsePostsList(self,response):

        sel = Selector(response)
        posts = sel.xpath('//div[@class="vt_post_holder"]')
        items = []
        condition = "hiv"
        topic = response.xpath('//h1[@class="caps"]/text()').extract_first()
        url = response.url
        for post in posts:
            item = PostItemsList()
            item['author'] = post.xpath('.//span[@class="vt_asked_by_user"]/a/text()').extract_first()
            item['author_link']=post.xpath('.//span[@class="vt_asked_by_user"]/a/@href').extract_first()

            if not item['author']:
                item['author'] = post.xpath('.//div[@class="vt_asked_by_user"]/a/text()').extract_first()
                item['author_link']=post.xpath('.//div[@class="vt_asked_by_user"]/a/@href').extract_first()

            item['create_date'] = post.xpath('.//span[@class="vt_first_timestamp"]/text()').extract_first()
            if not item['create_date']:
                item['create_date'] = post.xpath('.//div[@class="vt_reply_timestamp"]/text()').extract_first().replace('replied','').strip()

            item['post'] = re.sub('\s+',' '," ".join(post.xpath('.//div[@class="vt_post_body"]/text()').extract()).replace("\t","").replace("\n","").replace("\r",""))
            item['tag']=''
            item['topic'] = topic
            item['url']=url
            logging.info(item.__str__)
            items.append(item)
        return items
