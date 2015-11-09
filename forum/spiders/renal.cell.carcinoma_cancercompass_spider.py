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
    name = "renal.cell.carcinoma_cancercompass_spider"
    allowed_domains = ["cancercompass.com"]
#    start_urls = [
#        "http://www.healingwell.com/community/default.aspx?f=23&m=1001057",
#    ]
    start_urls = [
        "http://www.cancercompass.com/message-board/cancers/renal-cell-cancer/1,0,119,131.htm?sortby=replies&dir=1",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                restrict_xpaths='//table[contains(@class, "mbDis")]//a[contains(@class, "subLink")]',
                canonicalize=True,
                ), callback='parsePost', follow=True),

            # Rule to follow arrow to next product grid
            # Rule(LinkExtractor(
            #     restrict_xpaths='//*[@id="MainContent_ContentPlaceHolder1_discussionList_dtpDis"]',
            #     canonicalize=True,
            #     #allow='http://www.cancerforums.net/threads/',
            # ), follow=True),
            Rule(LinkExtractor(
                restrict_xpaths='//*[@id="MainContent_ContentPlaceHolder1_messageList1_pnlTopPager"]',
                canonicalize=True,
                #allow='http://www.cancerforums.net/threads/',
            ), callback='parsePost', follow=True),
        )

    # https://github.com/scrapy/dirbot/blob/master/dirbot/spiders/dmoz.py
    # https://github.com/scrapy/dirbot/blob/master/dirbot/pipelines.py
    def parsePost(self,response):
        logging.info(response)
        sel = Selector(response)
        posts = sel.css('.mbpost')
        items = []
        topic = sel.css('.contentText').xpath('./h1/text()').extract()[0].strip()
        url = response.url
        condition="Renal Cell Carcinoma"
        for post in posts:
            if len(post.xpath('./div[1]/p/a'))==0:
                continue
            item = PostItemsList()
            item['author'] = self.parseText(str=post.xpath('./div[1]/p/a').extract()[0].strip())
            item['author_link']=response.urljoin(post.xpath('./div[1]/p/a/@href').extract()[0])
            item['condition']=condition
            item['create_date'] = self.parseText(str=post.xpath('./div[2]/div[1]/p/text()').extract()[1].strip()[2:])
            post_msg=self.parseText(str=post.css('.msgContent').extract()[0])
            item['post']=post_msg
            item['tag']=''
            item['topic'] = topic
            item['url']=url
            logging.info(post_msg)
            items.append(item)
        return items

    def parseText(self, str):
        soup = BeautifulSoup(str, 'html.parser')
        return re.sub(" +|\n|\r|\t|\0|\x0b|\xa0",' ',soup.get_text()).strip()
