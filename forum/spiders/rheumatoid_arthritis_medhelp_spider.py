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
    name = "rheumatoid_arthritis_medhelp_spider"
    allowed_domains = ["medhelp.org"]
#    start_urls = [
#        "http://www.healingwell.com/community/default.aspx?f=23&m=1001057",
#    ]
    start_urls = [
        "http://www.medhelp.org/forums/Rheumatoid-Arthritis/show/377",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                restrict_xpaths='//div[contains(@class,"subjects_list")]/div',
                canonicalize=True,
                ), callback='parsePost', follow=True),
            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                restrict_xpaths='//*[@id="pagination_nav"]',
            ), callback='parsePost', follow=True),
        )

    # https://github.com/scrapy/dirbot/blob/master/dirbot/spiders/dmoz.py
    # https://github.com/scrapy/dirbot/blob/master/dirbot/pipelines.py
    def parsePost(self,response):
        logging.info(response)
        sel = Selector(response)
        posts = sel.xpath('//*[@id="post_answer_body"]/div')
        items = []
        if len(posts)==0:
            return items
        topic = sel.css('.question_title').xpath('./text()').extract()[0].strip()
        url = response.url

        item = PostItemsList()
        post=sel.xpath('//*[@id="post_question_header"]')
        item['author'] = self.parseText(str=post.css('.post_byline').xpath('./a').extract()[0].strip())
        item['author_link']=response.urljoin(post.css('.post_byline').xpath('./a/@href').extract()[0])
        item['create_date'] = self.parseText(post.css('.post_byline').xpath('./span[3]/text()').extract()[0])
        post_msg=self.parseText(str=post.css('.post_message_container').xpath('./div[1]').extract()[0])
        item['post']=post_msg
        item['tag']='rheumatoid arthritis'
        item['topic'] = topic
        item['url']=url
        logging.info(post_msg)
        items.append(item)

        for post in posts:
            item = PostItemsList()
            if len(post.css('.post_message_container'))==0:
                continue
            item['author'] = self.parseText(str=post.css('.post_byline').xpath('./a').extract()[0].strip())
            item['author_link']=response.urljoin(post.css('.post_byline').xpath('./a/@href').extract()[0])
            item['create_date'] = self.parseText(post.css('.post_byline').xpath('./span[3]/text()').extract()[0])
            post_msg=self.parseText(str=post.css('.post_message_container').xpath('./div[1]').extract()[0])
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