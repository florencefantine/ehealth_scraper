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
    name = "epilepsy_copingwithepilepsy_spider"
    allowed_domains = ["www.coping-with-epilepsy.com"]
    start_urls = [
        "http://www.coping-with-epilepsy.com/forums/f20/",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                    restrict_xpaths='//a[contains(@id,"thread_title")]',
                    canonicalize=True,
                ), callback='parsePostsList'),
            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                    restrict_xpaths='//a[@rel="next"][last()]',
                    canonicalize=True,
                ), follow=True),
        )

    # https://github.com/scrapy/dirbot/blob/master/dirbot/spiders/dmoz.py
    # https://github.com/scrapy/dirbot/blob/master/dirbot/pipelines.py
    def parsePostsList(self,response):
        sel = Selector(response)

        posts = sel.xpath('//div[@id="posts"]//div[@class="page"]')
        items = []
        condition="epilepsy"
        topic = response.xpath('//h1/strong/text()').extract_first().strip()
        url = response.url
        for post in posts:
            item = PostItemsList()
            item['author'] = post.xpath('.//a[@class="bigusername"]/text()').extract_first()
            if not item['author']:
                item['author'] = post.xpath('.//a[@class="bigusername"]/font/text()').extract_first()
            if not item['author']:
                item['author'] = post.xpath('.//a[@class="bigusername"]/b/font/text()').extract_first()
            item['author_link'] = post.xpath('.//a[@class="bigusername"]/@href').extract_first()
            item['condition']=condition
            item['create_date'] = post.xpath('.//td[@class="thead"]/div[2]').extract_first()
            p = re.compile(r'<.*?>')
            item['create_date'] = p.sub('',item['create_date']).strip()
            item['post'] = re.sub('\s+',' '," ".join(post.xpath('.//td[@class="alt1"]/div/text()').extract()).replace("\t","").replace("\n","").replace("\r",""))
            item['tag'] ='epilepsy'
            item['topic'] = topic
            item['url'] = url
            logging.info(item.__str__)
            items.append(item)
        return items
