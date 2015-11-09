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
    name = "epilepsy_topix_spider"
    allowed_domains = ["www.topix.com"]
    start_urls = [
        "http://www.topix.com/forum/health/epilepsy",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                    restrict_xpaths='//a[@class="threadtitle"]',
                    canonicalize=True,
                ), callback='parsePostsList'),
            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                    restrict_xpaths='//a[@data-t="forum-next"][last()]',
                    canonicalize=True,
                ), follow=True),
        )

    # https://github.com/scrapy/dirbot/blob/master/dirbot/spiders/dmoz.py
    # https://github.com/scrapy/dirbot/blob/master/dirbot/pipelines.py
    def parsePostsList(self,response):
        sel = Selector(response)
        posts = sel.xpath('//table[@class="post_table"]//tr')
        items = []
        topic = response.xpath('//h1/text()').extract_first()
        url = response.url
        condition='epilepsy'
        for post in posts:
            item = PostItemsList()
            item['create_date'] = post.xpath('.//span[@class="x-post-time"]/text()').extract_first()
            if item['create_date']:
                item['author'] = post.xpath('.//div[@class="authorsn x-author"]/text()').extract_first()
                item['author_link'] = '' 
                if not item['author']:
                    item['author'] = post.xpath('.//a[@data-t="post-usersntxt"]/text()').extract_first()
                    item['author_link'] = post.xpath('.//a[@data-t="post-usersntxt"]/@href').extract_first()
                item['condition']=condition
                item['post'] = re.sub('\s+',' '," ".join(post.xpath('.//div[@class="x-post-content"]/text()').extract()).replace("\t","").replace("\n","").replace("\r",""))
                item['tag']='epilepsy'
                item['topic'] = topic
                item['url']=url
                logging.info(item.__str__)
                items.append(item)
        return items
