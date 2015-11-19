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
    name = "hiv_topix_spider"
    allowed_domains = ["topix.com"]
#    start_urls = [
#        "http://www.healingwell.com/community/default.aspx?f=23&m=1001057",
#    ]
    start_urls = [
        "http://www.topix.com/forum/health/hiv-aids",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                restrict_xpaths='//table[contains(@class,"thread_table")]/tr',
                canonicalize=True,
                deny='http://www.topix.com/member/profile/',
                ), callback='parsePost', follow=True),
            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                restrict_xpaths="//a[contains(@class, 'x-thread-pagination')]",
                deny='http://www.topix.com/member/profile/',
            ), callback='parsePost', follow=True),
        )

    # https://github.com/scrapy/dirbot/blob/master/dirbot/spiders/dmoz.py
    # https://github.com/scrapy/dirbot/blob/master/dirbot/pipelines.py
    def parsePost(self,response):
        logging.info(response)
        sel = Selector(response)
        posts = sel.css(".post_table").xpath('./tr')
        items = []
        if len(posts)==0:
            return items
        topic = response.xpath('//div[contains(@class,"str-forum-header")]/h1/text()').extract()[0]
        url = response.url
        for post in posts:
            item = PostItemsList()
            if len(post.css('.regsn'))>0:
                item['author'] = post.css('.regsn').xpath('./a/text()').extract()[0]
                item['author_link']=response.urljoin(post.css('.regsn').xpath('./a/@href').extract()[0])
            elif len(post.css('.x-author'))>0:
                item['author'] = post.css('.x-author').xpath("text()").extract()[0]
                item['author_link']=''
            else:
                continue
            item['create_date']= self.parseText(str=post.css('.x-comment-info').extract()[0])
            post_msg= self.parseText(str=post.css('.x-post-content').extract()[0])
            item['post']=post_msg
            item['tag']='hiv'
            item['topic'] = topic
            item['url']=url
            logging.info(post_msg)
            items.append(item)
        return items

    def parseText(self, str):
        soup = BeautifulSoup(str, 'html.parser')
        return re.sub(" +|\n|\r|\t|\0|\x0b|\xa0",' ',soup.get_text()).strip()