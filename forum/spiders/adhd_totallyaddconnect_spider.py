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
    name = "adhd_totallyaddconnect_spider"
    allowed_domains = ["totallyaddconnect.com"]
    start_urls = [
        "http://www.totallyaddconnect.com/forums",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                    restrict_xpaths='//td[@class="bbp-topic-title"]',
                    canonicalize=True,
                ), callback='parsePostsList'),
            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                    restrict_xpaths='//td[@class="bbp-forum-info"]',
                    canonicalize=True,
                    deny=(r'user_profile_*\.html',)
                ), follow=True),
            Rule(LinkExtractor(
                    restrict_xpaths='//td[@class="bbp-forum-title"]',
                    canonicalize=True,
                    deny=(r'user_profile_*\.html',)
                ), follow=True),
            Rule(LinkExtractor(
                    restrict_xpaths='//a[@class="page-numbers"]',
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
        #posts = sel.css(".vt_post_holder")
        posts = sel.xpath('//table[@class="bbp-replies"]')
        items = []
        topic = ''.join(sel.xpath('//h1[@class="entry-title"]/text()').extract()).strip()
        url = response.url
        condition="adhd"
            
        item = PostItemsList()
        item['author'] = sel.xpath('//table[@class="bbp-topic"]//a[@class="bbp-author-name"]/text()').extract_first()
        item['author_link'] = sel.xpath('//table[@class="bbp-topic"]//a[@class="bbp-author-name"]/@href').extract_first()
        item['condition'] = condition
        #create_date = ''.join(sel.xpath('//span[@class="post-meta"]/text()').extract()).replace("Posted by","").replace("to","")
        create_date = ''.join(sel.xpath('//table[@class="bbp-topic"]//tr[@class="bbp-topic-header"]//text()').extract()).strip()
        item['create_date']= self.cleanText(create_date)
        
        message = ''.join(sel.xpath('//td[@class="bbp-topic-content"]//text()').extract())
        item['post'] = self.cleanText(message)
        item['tag']='adhd'
        item['topic'] = topic
        item['url']=url
        logging.info(item.__str__)
        items.append(item)

        for post in posts:
            item = PostItemsList()
            item['author'] = post.xpath('.//a[@class="bbp-author-name"]/text()').extract_first()
            item['author_link'] = post.xpath('.//a[@class="bbp-author-name"]/@href').extract_first()
            item['condition'] = condition
            create_date = ''.join(post.xpath('.//tr[@class="bbp-reply-header"]//text()').extract()).strip()
            item['create_date']= self.cleanText(create_date)
            
            message = ''.join(post.xpath('.//td[@class="bbp-reply-content"]//text()').extract())
            item['post'] = self.cleanText(message)
            item['tag']=''
            item['topic'] = topic
            item['url']=url
            logging.info(item.__str__)
            items.append(item)
        return items
