import scrapy
from scrapy.contrib.spiders import Spider, Rule, Request
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.selector import Selector
from forum.items import PostItemsList
import re
import logging
from bs4 import BeautifulSoup
from selenium import webdriver
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
class ForumsSpider(Spider):
    name = "rheumatoid_arthritis_patientinfo_spider"
    allowed_domains = ["patient.info"]
#    start_urls = [
#        "http://www.healingwell.com/community/default.aspx?f=23&m=1001057",
#    ]
    start_urls = [
        "http://patient.info/forums/discuss/browse/rheumatoid-arthritis-1968",
    ]

    # rules = (
    #         # Rule to go to the single product pages and run the parsing function
    #         # Excludes links that end in _W.html or _M.html, because they point to
    #         # configuration pages that aren't scrapeable (and are mostly redundant anyway)
    #         Rule(LinkExtractor(
    #             restrict_xpaths='//ul[contains(@class, "thread-list")]/li//h3[contains(@class, "title")]',
    #             canonicalize=True,
    #             allow='http://patient.info/forums/forums/discuss',
    #             ), callback='parsePost', follow=True),
    #
    #         # Rule to follow arrow to next product grid
    #         Rule(LinkExtractor(
    #             restrict_xpaths='//*[@id="group-discussions"]/form[1]/a',
    #             allow='http://patient.info/forums/forums/discuss',
    #             canonicalize=True,
    #         ), follow=True),
    #         # Rule(LinkExtractor(
    #         #     restrict_xpaths='//*[@id="col1"]/div[2]/div[2]/div[1]/table/tr[3]/td[1]/a[1]/@href',
    #         # ), follow=True),
    #     )

    # Place your webdriver here:
    driver = webdriver.PhantomJS()
    # driver = webdriver.Chrome('G:\\tools\\chromedriver.exe')
    # https://github.com/scrapy/dirbot/blob/master/dirbot/spiders/dmoz.py
    # https://github.com/scrapy/dirbot/blob/master/dirbot/pipelines.py

    def parse(self, response):
        self.driver.get(response.url)
        el = Selector(text=self.driver.page_source).xpath('//ul[contains(@class, "thread-list")]/li//h3[contains(@class, "title")]/a/@href')
        requestList=[]
        for r in el.extract():
            requestList.append(Request(response.urljoin(r), callback=self.parsePost))

        el = Selector(text=self.driver.page_source).xpath('//*[@id="group-discussions"]/form[1]/a')
        for r in el.extract():
            requestList.append(Request(response.urljoin(r), callback=self.parsePost))

        if len(requestList)>0:
            return requestList
        self.driver.close()

    def parsePost(self,response):
        logging.info(response)
        self.driver.get(response.url)
        sel = Selector(text=self.driver.page_source)
        posts = sel.xpath('//ul[contains(@class, "replies")]/li')
        items = []
        topic = sel.xpath('//*[@id="topic"]/article/h1/text()').extract()[0]
        url = response.url
        post = sel.xpath('//*[@id="topic"]')
        item = PostItemsList()
        item['author'] = post.xpath('./div/a/p/strong[2]/text()').extract()[0].strip()
        item['author_link']=response.urljoin(post.xpath("./div/a/@href").extract()[0])
        item['create_date']= self.parseText(str=post.xpath('./article/span/time/@title').extract()[0])
        post_msg=self.parseText(str=post.xpath('./article/div/p').extract()[0])
        item['post']=post_msg
        item['tag']='rheumatoid arthritis'
        item['topic'] = topic
        item['url']=url
        logging.info(post_msg)
        items.append(item)

        for post in posts:
            item = PostItemsList()
            if len(post.css('.avatar')) == 0:
                continue
            item['author'] = post.xpath("./article/span[1]/a[1]/text()").extract()[0].strip()
            item['author_link']=response.urljoin(post.xpath("./article/span[1]/a[1]/@href").extract()[0])
            item['create_date']= self.parseText(str=post.xpath('./article/span[2]/time/@title').extract()[0])
            post_msg=self.parseText(str=post.xpath('./article/div[1]/p').extract()[0])
            item['post']=post_msg
            item['tag']='rheumatoid arthritis'
            item['topic'] = topic
            item['url']=url
            logging.info(post_msg)
            items.append(item)
        return items

    def parseText(self, str):
        soup = BeautifulSoup(str, 'html.parser')
        return re.sub(" +|\n|\r|\t|\0|\x0b|\xa0",' ',soup.get_text()).strip()