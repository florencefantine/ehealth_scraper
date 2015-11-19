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
    name = "hiv_medhelp_spider"
    allowed_domains = ["www.medhelp.org"]
    start_urls = [
        "http://www.medhelp.org/forums/HIV---Prevention/show/117",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                    restrict_xpaths='//div[@class="fonts_resizable_subject subject_title "]/a',
                ), callback='parsePostsList'),

            

            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                    restrict_xpaths='//div[@id="pagination_nav"]/a[@class="msg_next_page"]'
                ), follow=True),
        )

    # https://github.com/scrapy/dirbot/blob/master/dirbot/spiders/dmoz.py
    # https://github.com/scrapy/dirbot/blob/master/dirbot/pipelines.py
    def parsePostsList(self,response):
        sel = Selector(response)
        posts = sel.xpath('//div[@class="post_message_container"]')
        condition = "hiv"
        items = []
        topic = response.xpath('//div[@class="question_title"]/text()').extract_first().strip()
        url = response.url
        for post in posts:
            item = PostItemsList()
            item['author'] = post.xpath('.//div[@class="post_byline"]/a/text()').extract_first()
            item['author_link'] = post.xpath('.//div[@class="post_byline"]/a/@href').extract_first()
            item['condition'] = condition
            item['create_date'] = post.xpath('.//div[@class="post_byline"]/span[@class="byline_date"]/text()').extract_first()
            item['post'] = re.sub('\s+',' '," ".join(post.xpath('.//div[@class="post_message fonts_resizable"]/text()').extract()).replace("\t","").replace("\n","").replace("\r",""))
            item['tag']=''
            item['topic'] = topic
            item['url']=url
            logging.info(item.__str__)
            items.append(item)
        return items
