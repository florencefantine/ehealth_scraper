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
    name = "breastcancer_forumtnbcfoundation_spider"
    allowed_domains = ["tnbcfoundation.org"]
    start_urls = [
        "http://forum.tnbcfoundation.org/",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                    restrict_xpaths='//a[contains(@href,"topic")]',
                    canonicalize=True,
                ), callback='parsePostsList'),
            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                    restrict_xpaths='//a[contains(@href,"forum")]',
                    canonicalize=True,
                    deny=(r'memuser_profile_*\.html',)
                ), follow=True),
            Rule(LinkExtractor(
                    restrict_xpaths='//a[@class="pageLink"]',
                    canonicalize=True,
                    deny=(r'memuser_profile_*\.html',)
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
        #posts = sel.xpath('//div[@class="entry unvoted"]')
        items = []
        topic = ''.join(response.xpath('//h1/text()').extract())
        url = response.url
        condition="breast cancer"
        
        #for post in posts:
        author = sel.xpath('//span[contains(@id, "userProfile")]/text()').extract()
        author_link = sel.xpath('//div[@class="dropDownMenu"]/a[contains(@href,"member")]/@href').extract()
        condition = condition
        create_date= sel.xpath('//td[contains(@class,"TableTop")]/text()').extract()
        message = sel.xpath('//div[@class="msgBody"]//text()').extract()

        for i in range(len(author)):
            item = PostItemsList()
            item['author'] = author[i]
            item['author_link'] = author_link[i]
            item['condition'] = condition
            item['create_date'] = self.cleanText(create_date[i])    
            item['post'] = self.cleanText(message[i])
            item['tag']=''
            item['topic'] = topic
            item['url']=url            
            logging.info(item.__str__)
            items.append(item)
        return items
