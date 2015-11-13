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
    name = "hiv_healthboards_spider"
    allowed_domains = ["www.healthboards.com"]
    start_urls = [
        "http://www.healthboards.com/boards/hiv-prevention/",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                    restrict_xpaths='//a[contains(@id,"thread_title")]',
                ), callback='parsePostsList'),
            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                    restrict_xpaths='//a[@rel="next"][last()]'
                ), follow=True),
        )

    # https://github.com/scrapy/dirbot/blob/master/dirbot/spiders/dmoz.py
    # https://github.com/scrapy/dirbot/blob/master/dirbot/pipelines.py
    def parsePostsList(self,response):
        sel = Selector(response)
        posts = sel.xpath('//div[contains(@id,"edit")]')
        items = []
        condition = "hiv"
        topic = response.xpath('//div[@class="navbar"]/strong/text()').extract_first().strip()
        url = response.url
        for post in posts:
            item = PostItemsList()
            item['author'] = post.xpath('.//div[contains(@id,"postmenu")]/text()').extract_first().strip()
            item['author_link'] = ''
            item['condition'] = condition
            item['create_date'] = post.xpath('.//td[@class="thead"][1]').extract_first()
            p = re.compile(r'<.*?>')
            item['create_date'] = p.sub('',item['create_date']).strip()

            item['post'] = re.sub('\s+',' '," ".join(post.xpath('.//div[contains(@id,"post_message")]/text()').extract()).replace("\t","").replace("\n","").replace("\r",""))
            item['tag']=''
            item['topic'] = topic
            item['url']=url
            logging.info(item.__str__)
            items.append(item)
        return items
