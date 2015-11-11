import scrapy
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.selector import Selector
from forum.items import PostItemsList
import re
import logging
from bs4 import BeautifulSoup

## LOGGING to file
#import logging
#from scrapy.log import ScrapyFileLogObserver

#logfile = open('testlog.log', 'w')
#log_observer = ScrapyFileLogObserver(logfile, level=logging.DEBUG)
#log_observer.start()


# Spider for crawling multiple-sclerosis board
class ForumsSpider(CrawlSpider):
    name = "multiplesclerosis_inspire_spider"
    allowed_domains = ["inspire.com"]
    start_urls = [
        "https://www.inspire.com/search/?query=multiple+sclerosis",
    ]

    rules = (
            Rule(LinkExtractor(
                restrict_xpaths='//*[@id="search-results"]/h3',
                canonicalize=True,
                allow='http.://(www\.)?inspire.com/groups/.*',
                ), callback='parsePost', follow=False),
        )

    def cleanText(self,text):
        soup = BeautifulSoup(text,'html.parser')
        text = soup.get_text();
        text = re.sub("( +|\n|\r|\t|\0|\x0b|\xa0|\xbb|\xab)+",' ',text).strip()
        return text 

    def parseText(self, str):
        soup = BeautifulSoup(str, 'html.parser')
        return re.sub(" +|\n|\r|\t|\0|\x0b|\xa0",' ',soup.get_text()).strip()

    def parsePost(self,response):
        #logging.info(response)
        sel = Selector(response)
        items = []
        topic = self.cleanText(response.xpath('//*[@class="post-title"]').extract()[0].encode('ascii'))
        url = response.url

        #start message
        item = PostItemsList()
        post_info = sel.xpath('//*/div[@class="post-info"]')
        item['author'] = self.cleanText(post_info.xpath('//*/li[@class="by"]/a').extract()[0])
        item['author_link'] = post_info.xpath('//*/li[@class="by"]/a/@href').extract()[0]
        item['create_date'] = self.cleanText(post_info.xpath('//*/ul/li[@class="by"]').extract()[0]).split(u'\xb7')[1].strip()
        item['post'] = post_info.xpath('//*[@class="post-body"]').extract()[0]
        item['tag'] = 'multiple-sclerosis'
        item['topic'] = topic
        item['url'] = url
        items.append(item)

        posts = sel.xpath('//*/div[@class="comments-box"]')
        if not posts: return items
        for post in posts:
            post_xp = post.xpath('./p')
            if not post_xp: continue
            post_msg = self.parseText(str=post_xp.extract()[0])

            item = PostItemsList()
            item['author'] = self.cleanText(post.xpath('./div/ul/li[1]/a').extract()[0])
            item['author_link'] = post.xpath('./div/ul/li[1]/a/@href').extract()[0]
            item['create_date'] = self.cleanText(post.xpath('./div/ul/li[3]').extract()[0])
            item['post'] = post_msg
            item['tag'] = 'multiple-sclerosis'
            item['topic'] = topic
            item['url'] = url
            #logging.info(post_msg)
            items.append(item)

        return items

