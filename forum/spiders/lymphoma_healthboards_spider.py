import scrapy
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.selector import Selector
from forum.items import PostItemsList
from bs4 import BeautifulSoup
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
    name = "lymphoma_healthboards_spider"
    allowed_domains = ["www.healthboards.com"]
    start_urls = [
        "http://www.healthboards.com/boards/lymphomas/",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                    restrict_xpaths='//a[contains(@id,"thread_title")]',
                    canonicalize=True,
                ), callback='parsePostsList'),
            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                    restrict_xpaths='//a[@rel="next"][last()]',
                    canonicalize=True,
                ), follow=True),
        )

    def cleanText(self,text):
        soup = BeautifulSoup(text,'html.parser')
        text = soup.get_text();
        text = re.sub("( +|\n|\r|\t|\0|\x0b|\xa0|\xbb|\xab)+",' ',text).strip()
        return text 

    def parsePostsList(self, response):
        print(response.url)
        items = []
        sel = Selector(response)
        condition = sel.css(".navbar").xpath("./span[2]/a/text()").extract()[0]
        subject = response.xpath(
            '//div[@class="navbar"]/strong/text()').extract()[0]
        subject = subject.strip()
        url = response.url
        posts = response.xpath('//table[contains(@id, "post")]')

        for post in posts:
            item = PostItemsList()
            author = post.xpath(
                './/div[contains(@id, "postmenu")]/text()').extract()[0]
            author = author.strip()
            author_link = "*"
            create_date = post.xpath(
                './/td[@class="thead"]//text()'
            ).extract()[1].strip()

            message = ''.join(post.xpath(
                './/div[contains(@id, "post_message_")]//text()'
            ).extract())
            message = self.cleanText(message)

            item['author'] = author
            item['author_link'] = author_link
            item['condition'] = condition
            item['create_date'] = create_date
            item['post'] = message
            item['tag'] = ''
            item['topic'] = subject
            item['url'] = url

            items.append(item)
        return items

    # https://github.com/scrapy/dirbot/blob/master/dirbot/spiders/dmoz.py
    # https://github.com/scrapy/dirbot/blob/master/dirbot/pipelines.py
    '''
    def parsePostsList(self,response):
        sel = Selector(response)
        posts = sel.xpath('//div[contains(@id,"edit")]')
        condition = sel.css(".navbar").xpath("./span[2]/a/text()").extract()[0]
        items = []
        topic = response.xpath('//div[@class="navbar"]/strong/text()').extract_first().strip()
        url = response.url
        for post in posts:
            item = PostItemsList()
            item['author'] = post.xpath('.//div[contains(@id,"postmenu")]/text()').extract_first().strip()
            item['author_link'] = ''
            item['condition'] = condition
            item['create_date'] = post.xpath('.//td[@class="thead"][1]').extract_first()
            p = re.compile(r'<.*?>')
            item['create_date'] = p.sub('',item['create_date']).strip()

            item['post'] = re.sub('\s+',' '," ".join(post.xpath('.//div[contains(@id,"post_message")]/text()').extract()).replace("\t","").replace("\n","").replace("\r",""))
            item['tag']=''
            item['topic'] = topic
            item['url']=url
            logging.info(item.__str__)
            items.append(item)
        return items
    '''
