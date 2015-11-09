import scrapy
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.selector import Selector
from forum.items import PostItemsList
import re
import logging

## LOGGING to file
#import logging
#from scrapy.log import ScrapyFileLogObserver

#logfile = open('testlog.log', 'w')
#log_observer = ScrapyFileLogObserver(logfile, level=logging.DEBUG)
#log_observer.start()

# Spider for crawling Adidas website for shoes
class ForumsSpider(CrawlSpider):
    name = "epilepsy_ehealthforums_spider"
    allowed_domains = ["ehealthforum.com"]
    start_urls = [
        "http://ehealthforum.com/health/epilepsy.html",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                    restrict_xpaths='//a[contains(@class,"topictitle")]',
                    canonicalize=True,
                ), callback='parsePostsList'),
            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                    restrict_xpaths='//a[@class="pagination_number"]',
                    canonicalize=True,
                    deny=(r'user_profile_*\.html',)
                ), follow=True),
        )

    # https://github.com/scrapy/dirbot/blob/master/dirbot/spiders/dmoz.py
    # https://github.com/scrapy/dirbot/blob/master/dirbot/pipelines.py
    def parsePostsList(self,response):
        sel = Selector(response)
        posts = sel.css(".vt_post_holder")
        items = []
        topic = response.css('h1.caps').xpath('text()').extract()[0]
        url = response.url
        condition="epilepsy"
        for post in posts:
            item = PostItemsList()
            item['author'] = post.css('.vt_asked_by_user').xpath("./a").xpath("text()").extract()[0]
            item['author_link']=post.css('.vt_asked_by_user').xpath("./a").xpath("@href").extract()[0]
            item['condition']=condition
            item['create_date']= post.css('.vt_first_timestamp').xpath('text()').extract().extend(response.css('.vt_reply_timestamp').xpath('text()').extract())
            item['post'] = re.sub('\s+',' '," ".join(post.css('.vt_post_body').xpath('text()').extract()).replace("\t","").replace("\n","").replace("\r",""))
            item['tag']='epilepsy'
            item['topic'] = topic
            item['url']=url
            logging.info(item.__str__)
            items.append(item)
        return items
