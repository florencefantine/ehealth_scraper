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
    name = "renal.cell.carcinoma_cancerorg_spider"
    allowed_domains = ["cancer.org"]
#    start_urls = [
#        "http://www.healingwell.com/community/default.aspx?f=23&m=1001057",
#    ]
    start_urls = [
        "http://csn.cancer.org/forum/142",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                restrict_xpaths='//tr[contains(@class, "odd")]//td[contains(@class, "title")]',
                canonicalize=True,
                ), callback='parsePost', follow=True),

            Rule(LinkExtractor(
                restrict_xpaths='//tr[contains(@class, "even")]//td[contains(@class, "title")]',
                canonicalize=True,
                ), callback='parsePost', follow=True),

            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                restrict_xpaths='//li[contains(@class, "pager-item")]',
                canonicalize=True,
                deny='http://csn.cancer.org/node/',
                #allow='http://www.cancerforums.net/threads/',
            ), follow=True),

            Rule(LinkExtractor(
                restrict_xpaths='//li[contains(@class, "pager-item")]',
                canonicalize=True,
                deny='http://csn.cancer.org/forum/'
                #allow='http://www.cancerforums.net/threads/',
            ), callback='parsePost', follow=True),
        )

    # https://github.com/scrapy/dirbot/blob/master/dirbot/spiders/dmoz.py
    # https://github.com/scrapy/dirbot/blob/master/dirbot/pipelines.py
    def parsePost(self,response):
        logging.info(response)
        sel = Selector(response)
        posts = sel.xpath('//*[@id="comments"]').css('.comment-forum')
        condition="Renal Cell Carcinoma"
        items = []
        topic = sel.xpath('//*[@id="squeeze"]/div/div/h2/text()').extract()[0].strip()
        url = response.url

        for post in posts:
            if len(post.css('.author'))==0:
                continue
            item = PostItemsList()
            item['author'] = self.parseText(str=post.css('.author').extract()[0].strip())
            item['author_link']=''
            item['condition']=condition
            item['create_date'] = self.parseText(str=post.css('.date').extract()[0].strip()[2:])
            post_msg=self.parseText(str=post.css('.content').extract()[0])
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
