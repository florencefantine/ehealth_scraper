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
    name = "carcinoid.cancer_netpatientfoundation_spider"
    allowed_domains = ["netpatientfoundation.org"]
#    start_urls = [
#        "http://www.healingwell.com/community/default.aspx?f=23&m=1001057",
#    ]
    start_urls = [
        "http://www.netpatientfoundation.org/forum/5_1.html",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                restrict_xpaths='//tr[contains(@class, "tbCel1")]/td[2]',
                canonicalize=True,
                ), callback='parsePost'),

            Rule(LinkExtractor(
                restrict_xpaths='//tr[contains(@class, "tbCel2")]/td[2]',
                canonicalize=True,
                ), callback='parsePost'),

            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                restrict_xpaths='/html/body/div[3]/table[5]/tr/td/span/b/a[contains(@class, "navCell")]',
            ), follow=True),
            
            Rule(LinkExtractor(
                restrict_xpaths='/html/body/div[3]/table[4]/tr/td/span/b/a[contains(@class, "navCell")]'
            ), callback='parsePost')
        )

    # https://github.com/scrapy/dirbot/blob/master/dirbot/spiders/dmoz.py
    # https://github.com/scrapy/dirbot/blob/master/dirbot/pipelines.py
    def parsePost(self,response):
        logging.info(response)
        sel = Selector(response)
        posts = sel.xpath("//*[@id=\"allMsgs\"]").css(".forumsmb")
        condition="Carcinoid Cancer"
        items = []
        topic = response.xpath('//h1[contains(@class, "headingTitle")]/text()').extract()[0]
        url = response.url
        for post in posts:
            item = PostItemsList()
            item['author'] = post.css('.username').xpath("./a/text()").extract()[0]
            item['author_link']=response.urljoin(post.css('.username').xpath("./a/@href").extract()[0])
            item['condition']=condition
            item['create_date']= re.sub(" +|\n|\r|\t|\0|\x0b|\xa0",' ',post.xpath('./tr[1]/td[3]/div/text()').extract()[1]).strip()
            post_msg=post.css('.postedText').xpath('text()').extract()[0]
            soup = BeautifulSoup(post_msg, 'html.parser')
            post_msg = re.sub(" +|\n|\r|\t|\0|\x0b|\xa0",' ',soup.get_text()).strip()
            item['post']=post_msg
            item['tag']=condition
            item['topic'] = topic
            item['url']=url
            logging.info(post_msg)
            items.append(item)
        return items
