import scrapy
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.selector import Selector
from forum.items import PostItemsList
import re
import logging
from bs4 import BeautifulSoup
# import lxml.html
# from lxml.etree import ParserError
# from lxml.cssselect import CSSSelector

## LOGGING to file
#import logging
#from scrapy.log import ScrapyFileLogObserver

#logfile = open('testlog.log', 'w')
#log_observer = ScrapyFileLogObserver(logfile, level=logging.DEBUG)
#log_observer.start()

# Spider for crawling Adidas website for shoes
class ForumsSpider(CrawlSpider):
    name = "renal.cell.carcinoma_healthboards_spider"
    allowed_domains = ["healthboards.com"]
#    start_urls = [
#        "http://www.healingwell.com/community/default.aspx?f=23&m=1001057",
#    ]
    start_urls = [
        "http://www.healthboards.com/boards/cancer-kidney/",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                restrict_xpaths='//*[@id="threadslist"]/tbody[2]/tr/td[3]/div[1]',
                canonicalize=True,
                ), callback='parsePost', follow=True),

            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                restrict_xpaths='//div[contains(@class, "pagenav")]',
                canonicalize=True,
                deny='http://www.healthboards.com/boards/images/',
            ), callback='parsePost', follow=True),
        )

    # https://github.com/scrapy/dirbot/blob/master/dirbot/spiders/dmoz.py
    # https://github.com/scrapy/dirbot/blob/master/dirbot/pipelines.py
    def parsePost(self,response):
        logging.info(response)
        sel = Selector(response)
        posts = sel.xpath('//*[@id="posts"]//div[contains(@class, "page")]')
        items = []
        topic = sel.xpath('/html/body/table/tr/td/div[2]/div/div[1]/font/b/text()').extract()[0].strip()
        url = response.url
        condition ='Renal Cell Carcinoma'
        for post in posts:
            if len(post.css('.alt2'))==0:
                continue
            item = PostItemsList()
            item['author'] = self.parseText(str=post.css('.alt2').xpath('./div/text()').extract()[0].strip())
            item['author_link']=''
            item['condition']=condition
            item['create_date'] = self.parseText(str=post.css('.thead').extract()[0].strip())
            post_msg=self.parseText(str=post.css('.alt1').xpath('./div[2]').extract()[0])
            item['post']=post_msg
            item['tag']=condition
            item['topic'] = topic
            item['url']=url
            logging.info(post_msg)
            items.append(item)
        return items

    def parseText(self, str):
        soup = BeautifulSoup(str, 'html.parser')
        return re.sub(" +|\n|\r|\t|\0|\x0b|\xa0",' ',soup.get_text()).strip()
