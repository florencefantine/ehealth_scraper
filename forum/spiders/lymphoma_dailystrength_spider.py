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
    name = "lymphoma_dailystrength_spider"
    allowed_domains = ["dailystrength.org"]
#    start_urls = [
#        "http://www.healingwell.com/community/default.aspx?f=23&m=1001057",
#    ]
    start_urls = [
        "http://www.dailystrength.org/c/Hodgkins-Lymphoma/forum",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                restrict_xpaths='//tr[contains(@class, "sectiontableentry2")]',
                canonicalize=True,
                deny='http://www.dailystrength.org/people/',
                ), callback='parsePost', follow=True),
            Rule(LinkExtractor(
                restrict_xpaths='//tr[contains(@class, "sectiontableentry1")]',
                deny='http://www.dailystrength.org/people/',
                canonicalize=True,
                ), callback='parsePost'),

            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                restrict_xpaths='//a[contains(@class, "medium")]',
                deny='http://www.dailystrength.org/people/',
                canonicalize=True,
            ), follow=True),
            # Rule(LinkExtractor(
            #     restrict_xpaths='//*[@id="col1"]/div[2]/div[2]/div[1]/table/tr[3]/td[1]/a[1]/@href',
            # ), follow=True),
        )


    def cleanText(self,text):
        soup = BeautifulSoup(text,'html.parser')
        text = soup.get_text();
        text = re.sub("( +|\n|\r|\t|\0|\x0b|\xa0|\xbb|\xab)+",' ',text).strip()
        return text 
    
    # https://github.com/scrapy/dirbot/blob/master/dirbot/spiders/dmoz.py
    # https://github.com/scrapy/dirbot/blob/master/dirbot/pipelines.py
    def parsePost(self,response):
        logging.info(response)
        sel = Selector(response)
        posts = sel.xpath('//*[@id="col1"]/div[2]/div[2]/div[1]/table[4]')
        items = []
        condition="Lymphoma"
        topic = sel.xpath('//div[contains(@class, "discussion_topic_header_subject")]/text()').extract()[0]
        url = response.url
        post = sel.xpath('//table[contains(@class, "discussion_topic")]')
        item = PostItemsList()
        item['author'] = post.css('.username').xpath("./a").xpath("text()").extract()[0].strip()
        item['author_link']=response.urljoin(post.css('.username').xpath("./a/@href").extract()[0])
        item['condition']=condition
        item['create_date']= re.sub(" +|\n|\r|\t|\0|\x0b|\xa0",' ',post.css('.discussion_text').xpath('./span/text()').extract()[0]).strip()
        post_msg=self.cleanText(post.css('.discussion_text').extract()[0])
        # soup = BeautifulSoup(post_msg, 'html.parser')
        # post_msg = re.sub(" +|\n|\r|\t|\0|\x0b|\xa0",' ',soup.get_text()).strip()
        item['post']=post_msg
        item['tag']=condition
        item['topic'] = topic
        item['url']=url
        logging.info(post_msg)
        items.append(item)

        for post in posts:
            item = PostItemsList()
            if len(post.css('.username')) == 0:
                continue
            item['author'] = post.css('.username').xpath("./a").xpath("text()").extract()[0].strip()
            item['author_link']=response.urljoin(post.css('.username').xpath("./a/@href").extract()[0])
            item['create_date']= re.sub(" +|\n|\r|\t|\0|\x0b|\xa0",' ',post.xpath('./tr[1]/td[2]/div/table/tr/td/span[2]/text()').extract()[0]).strip()
            post_msg=self.cleanText(post.css('.discussion_text').extract()[0])
            # soup = BeautifulSoup(post_msg, 'html.parser')
            # post_msg = re.sub(" +|\n|\r|\t|\0|\x0b|\xa0",' ',soup.get_text()).strip()
            item['post']=post_msg
            item['tag']='Lymphoma'
            item['topic'] = topic
            item['url']=url
            logging.info(post_msg)
            items.append(item)
        return items
