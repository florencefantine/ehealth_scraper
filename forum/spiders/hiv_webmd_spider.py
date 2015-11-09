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
    name = "hiv_webmd_spider"
    allowed_domains = ["exchanges.webmd.com","forums.webmd.com"]
    start_urls = [
        "http://exchanges.webmd.com/hiv-and-aids-exchange",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                restrict_xpaths="//div[contains(@class,'expert_fmt')]/span/a",
                canonicalize=True,
            ), callback='parsePost', follow=True),

            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                restrict_xpaths="//div[contains(@class, 'pages')]/a",
                canonicalize=True,
            ), callback='parsePost', follow=True),
        )

    def cleanText(self,text):
        soup = BeautifulSoup(text,'html.parser')
        text = soup.get_text();
        text = re.sub("( +|\n|\r|\t|\0|\x0b|\xa0|\xbb|\xab)+",' ',text).strip()
        return text

    def cleanDate(self,text):
        create_date = re.sub("document.write\(DateDelta\('",'',text) 
        create_date = re.sub("'\)\);",'',create_date) 

    # https://github.com/scrapy/dirbot/blob/master/dirbot/spiders/dmoz.py
    # https://github.com/scrapy/dirbot/blob/master/dirbot/pipelines.py
    def parsePost(self,response):
        logging.info(response)
        sel = Selector(response)

        posts = sel.css(".exchange-reply-container")
        items = []
        condition="hiv"
        topic = sel.xpath("//div[contains(@class,'first_item_title_fmt')]/text()").extract()[0]
        url = response.url

        #---------
        post = sel.xpath('//*[contains(@class,"exchange_thread_rdr")]')
        item = PostItemsList()
        item['author'] = post.xpath("//div[contains(@class,'post_hdr_fmt')]/a").xpath("text()").extract()[0].strip()
        item['author_link']=response.urljoin(post.css('.post_hdr_fmt').xpath("./a/@href").extract()[0])
        item['condition']=condition
        item['create_date']= self.cleanDate(post.xpath("//div[contains(@class,'first_posted_fmt')]/script/text()").extract()[0])
        item['post']=self.cleanText(post.css('.post_fmt').extract()[0])
        item['tag']=''
        item['topic'] = topic
        item['url']=url
        logging.info(post_msg)
        items.append(item)

        cnt=0
        for post in posts:
            if cnt>1 and ("forum" in url.split("/")):
                item = PostItemsList()
                try:
                    item['author'] = post.css('.post_hdr_fmt').xpath("./a[1]").xpath("text()").extract()[0].strip()
                    item['author_link']=response.urljoin(post.css('.post_hdr_fmt').xpath("./a[1]/@href").extract()[0])
                    item['create_date']= self.cleanDate(post.xpath("//div[contains(@class,'posted_fmt')]/script/text()").extract()[0])
                    post_msg=self.cleanText(post.css('.post_fmt').extract()[0])
                    item['post']=post_msg
                    item['tag']=''
                    item['topic'] = topic
                    item['url']=url
                    logging.info(post_msg)
                    items.append(item)
                except:
                    continue
                cnt+=1
        return items
