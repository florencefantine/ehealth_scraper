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
    name = "epilepsy_epilepsycom_spider"
    allowed_domains = ["www.epilepsy.com"]
    start_urls = [
        "http://www.epilepsy.com/connect/forums/diagnostic-dilemmas-and-testing",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                    restrict_xpaths='//div[@class="views-field views-field-title"]//a',
                    canonicalize=True,
                ), callback='parsePostsList'),
            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                    restrict_xpaths='//li[contains(@class,"pager-next")]/a',
                    canonicalize=True,
                ), follow=True),
        )

    # https://github.com/scrapy/dirbot/blob/master/dirbot/spiders/dmoz.py
    # https://github.com/scrapy/dirbot/blob/master/dirbot/pipelines.py
    def parsePostsList(self,response):
        items = []
        topic = response.xpath('//div[@class="panel-pane pane-node-title no-title block"]//h2/text()').extract_first()
        url = response.url
        condition="epilepsy"
        item = PostItemsList()
        item['author'] = response.xpath('//div[@class="panel-pane pane-node-author no-title block"]/div/div/text()').extract_first().strip()
        item['author_link'] = ''
        item['condition']=condition
        item['post'] = re.sub('\s+',' '," ".join(response.xpath('//div[@class="panel-pane pane-entity-field pane-node-field-body no-title block"]//div[@class="field-item even"]/p/text()').extract()).replace("\t","").replace("\n","").replace("\r",""))
        item['tag']='epilepsy'
        item['topic'] = topic
        item['url']=url
        logging.info(item.__str__)
        items.append(item)
        return items