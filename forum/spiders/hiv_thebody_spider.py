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
    name = "hiv_thebody_spider"
    allowed_domains = ["thebody.com"]
#    start_urls = [
#        "http://www.healingwell.com/community/default.aspx?f=23&m=1001057",
#    ]
    start_urls = [
        "http://www.thebody.com/Forums/AIDS/SafeSex/",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                restrict_xpaths='//*[@id="qna_list"]',
                canonicalize=True,
                ), callback='parsePost', follow=True),

            Rule(LinkExtractor(
                restrict_xpaths='//*[@id="modify_answer_list"]',
                canonicalize=True,
                ), follow=True),
        )

    # https://github.com/scrapy/dirbot/blob/master/dirbot/spiders/dmoz.py
    # https://github.com/scrapy/dirbot/blob/master/dirbot/pipelines.py
    def parsePost(self,response):
        logging.info(response)
        sel = Selector(response)
        items = []
        if len(sel.xpath('//*[@id="maincontent_forums"]/div[4]/table/tr[1]/td[3]/h1'))==0:
            return items
        topic = sel.xpath('//*[@id="maincontent_forums"]/div[4]/table/tr[1]/td[3]/h1/text()').extract()[0]
        url = response.url
        item = PostItemsList()
        item['author'] = ""
        item['author_link']=""
        date = sel.xpath('//*[@id="maincontent_forums"]/div[4]/table/tr[1]/td[3]/p[1]/text()').extract()[0]
        item['create_date']=date
        post_msg=sel.xpath('//*[@id="maincontent_forums"]/div[4]/table/tr[1]/td[3]/p[3]').extract()[0]
        soup = BeautifulSoup(post_msg, 'html.parser')
        post_msg = re.sub(" +|\n|\r|\t|\0|\x0b|\xa0",' ',soup.get_text()).strip()
        item['post']=post_msg
        item['tag']='hiv'
        item['topic'] = topic
        item['url']=url
        logging.info(post_msg)
        items.append(item)

        item = PostItemsList()
        item['author'] = sel.xpath('//*[@id="response"]/h1/text()').extract()[0]
        item['author_link']=""
        item['create_date'] = date
        post_msg = sel.xpath('//*[@id="response"]/p').extract()[0]
        soup = BeautifulSoup(post_msg, 'html.parser')
        post_msg = re.sub(" +|\n|\r|\t|\0|\x0b|\xa0",' ',soup.get_text()).strip()
        item['post']=post_msg
        item['tag']='hiv'
        item['topic'] = topic
        item['url']=url
        logging.info(post_msg)
        items.append(item)
        return items
