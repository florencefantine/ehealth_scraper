import scrapy
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.selector import Selector
from forum.items import PostItemsList
import re
from bs4 import BeautifulSoup
import logging

## LOGGING to file
#import logging
#from scrapy.log import ScrapyFileLogObserver

#logfile = open('testlog.log', 'w')
#log_observer = ScrapyFileLogObserver(logfile, level=logging.DEBUG)
#log_observer.start()

# Spider for crawling Adidas website for shoes
class ForumsSpider(CrawlSpider):
    name = "breastcancer_nosurrender_spider"
    allowed_domains = ["nosurrenderbreastcancersupportforum.com"]
    start_urls = [
        "http://www.nosurrenderbreastcancersupportforum.com/",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                    restrict_xpaths='//a[@class="thread_title"]',
                    canonicalize=True,
                ), callback='parsePostsList'),
            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                    restrict_xpaths='//a[@class="forum_title"]',
                    canonicalize=True,
                    deny=(r'user_profile_*\.html',)
                ), follow=True),
            Rule(LinkExtractor(
                    restrict_xpaths='//a[(@class,"table_bottom_txt"]',
                    canonicalize=True,
                    deny=(r'user_profile_*\.html',)
                ), follow=True),
        )

    def cleanText(self,text):
        soup = BeautifulSoup(text,'html.parser')
        text = soup.get_text();
        text = re.sub("( +|\n|\r|\t|\0|\x0b|\xa0|\xbb|\xab)+",' ',text).strip()
        return text 

    # https://github.com/scrapy/dirbot/blob/master/dirbot/spiders/dmoz.py
    # https://github.com/scrapy/dirbot/blob/master/dirbot/pipelines.py
    def parsePostsList(self,response):
        sel = Selector(response)
        posts = sel.xpath('//tr[contains(@class,"table_row")]')
        items = []
        topic = response.xpath('//title/text()').extract()
        url = response.url
        condition="breastcancer"
        
        for post in posts:
            item = PostItemsList()
            item['author'] = post.xpath('.//a[contains(@class,"username usergroup")]/text()').extract()
            item['author_link'] = post.xpath('.//a[contains(@class,"username usergroup")]/@href').extract()
            item['condition'] = condition
            
            item['create_date'] = post.xpath('.//span[contains(@id,"posted_date")]/text()').extract()
           
            message = ''.join(post.xpath('.//span[contains(@id,"post_message")]/text()').extract())
            item['post'] = self.cleanText(message)
            item['tag']='breastcancer'
            item['topic'] = topic
            item['url']=url
            logging.info(item.__str__)
            items.append(item)
        return items
