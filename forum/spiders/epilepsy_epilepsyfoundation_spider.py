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
    name = "epilepsy_epilepsyfoundation_spider"
    allowed_domains = ["epilepsyfoundation.ning.com"]
    start_urls = [
        "http://epilepsyfoundation.ning.com/forum/categories/living-with-epilepsy/listForCategory",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                    restrict_xpaths='//td[@class="xg_lightborder"]/h3/a',
                    canonicalize=True,
                ), callback='parsePostsList'),
            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                    restrict_xpaths='//ul[@class="pagination easyclear "]/li[last()-1]/a',
                    canonicalize=True,
                ), follow=True),
        )

    # https://github.com/scrapy/dirbot/blob/master/dirbot/spiders/dmoz.py
    # https://github.com/scrapy/dirbot/blob/master/dirbot/pipelines.py
    def parsePostsList(self,response):
        sel = Selector(response)
        posts = sel.xpath('//dl[@class="discussion clear i0 xg_lightborder"]')
        items = []
        condition="epilepsy"
        topic = response.xpath('//h1/text()').extract_first()
        url = response.url
        
        item = PostItemsList()
        item['author'] = response.xpath('//ul[@class="navigation byline"]/li/a[contains(@href,"profile")]/text()').extract_first()
        item['author_link'] = response.xpath('//ul[@class="navigation byline"]/li/a[contains(@href,"profile")]/@href').extract_first()
        item['condition'] = condition
        item['create_date'] = response.xpath('//div[@class="xg_module xg_module_with_dialog"]//ul[@class="navigation byline"]/li/a[@class="nolink"][2]/text()').extract_first().replace('on','').replace('in','').strip()
        
        item['post'] = re.sub('\s+',' '," ".join(response.xpath('//div[@class="xg_module xg_module_with_dialog"]//div[@class="xg_user_generated"]/p/text()').extract()).replace("\t","").replace("\n","").replace("\r",""))
        if not item['post']:
            item['post'] = re.sub('\s+',' '," ".join(response.xpath('//div[@class="xg_module xg_module_with_dialog"]//div[@class="xg_user_generated"]/text()').extract()).replace("\t","").replace("\n","").replace("\r",""))

        item['tag']='epilepsy'
        item['topic'] = topic
        item['url']=url
        logging.info(item.__str__)
        items.append(item)

        for post in posts:
            item = PostItemsList()
            item['author'] = post.xpath('./dt[@class="byline"]/a[contains(@href,"user")]/text()').extract_first()
            item['author_link'] = post.xpath('./dt[@class="byline"]/a[contains(@href,"user")]/@href').extract_first()
            item['create_date'] = post.xpath('./dt[@class="byline"]/span[@class="timestamp"]/text()').extract_first()
            item['post'] = re.sub('\s+',' '," ".join(post.xpath('.//div[@class="description"]/div[@class="xg_user_generated"]/p/text()').extract()).replace("\t","").replace("\n","").replace("\r",""))

            if not item['post']:
                item['post'] = re.sub('\s+',' '," ".join(post.xpath('.//div[@class="description"]/div[@class="xg_user_generated"]/text()').extract()).replace("\t","").replace("\n","").replace("\r",""))

            item['tag']='epilepsy'
            item['topic'] = topic
            item['url']=url
            logging.info(item.__str__)
            items.append(item)
        return items
