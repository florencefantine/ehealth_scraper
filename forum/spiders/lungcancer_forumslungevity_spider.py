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
    name = "lungcancer_forumslungevity_spider"
    allowed_domains = ["lungevity.org"]
    start_urls = [
        "http://forums.lungevity.org/index.php?/forum/19-general/",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                    restrict_xpaths='//a[@class="topic_title"]',
                    canonicalize=True,
                ), callback='parsePostsList'),
            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                    restrict_xpaths='//li[@class="page"]/a[contains(@href,"page")]',
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
        posts = sel.xpath('//div[@class="post_body")]')
        items = []
        topic = ''.join(sel.xpath('//h1[@class="ipsType_pagetitle"]/text()').extract())
        url = response.url
        condition="lungcancer"
        for post in posts:
            item = PostItemsList()
            item['author'] = ''.join(post.xpath('.//span[@class="author vcard"]/text()').extract())
            item['author_link'] = ''
            item['condition'] = condition
            item['create_date'] = ''.join(post.xpath('.//abbr[@class="published"]/text()').extract())
            #item['create_date']= self.cleanText(create_date) 
            
            message = ''.join(post.xpath('.//div[@div="post entry-content ")]/text()').extract())
            item['post'] = self.cleanText(message)
            item['tag']='lungcancer'
            item['topic'] = topic
            item['url']=url
            logging.info(item.__str__)
            items.append(item)
        return items
