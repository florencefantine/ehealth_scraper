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


# Spider for crawling healthboards.com, multiple-sclerosis board
class ForumsSpider(CrawlSpider):
    name = "multiplesclerosis_healthboards_spider"
    allowed_domains = ["healthboards.com"]
    start_urls = [
        "http://www.healthboards.com/boards/multiple-sclerosis/",
    ]

    rules = (
            Rule(LinkExtractor(
                restrict_xpaths='//table[contains(@id, "threadslist")]',
                canonicalize=True,
                allow='http://www\.healthboards\.com/boards/multiple-sclerosis/[0-9]+-',
                ), callback='parsePost'),
            # Rule to follow arrow to next grid
            Rule(LinkExtractor(
                restrict_xpaths='//*/a[starts-with(@title,"Next Page")]',
            ), callback='parsePost', follow=True),
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
        posts = sel.xpath('//*/table[starts-with(@id,"post")]')
        items = []
        if not posts: return items
        topic = self.cleanText(response.xpath('/html/body/table/tr/td/div[2]/div/div[1]/div[3]/strong').extract()[0])
        url = response.url
        for post in posts:
            post_xp = post.xpath("./tr[2]/td[2]/div[2]")
            if post_xp:
                post_msg = self.parseText(str=post_xp.extract()[0])
            else:
                # 'thank you' post
                #"http://www.healthboards.com/boards/multiple-sclerosis/975878-hello-looking-ms-doc-chicago.html"
                continue        
            item = PostItemsList()
            item['author'] = post.xpath('./div[starts-with(@id="postmenu")]').extract()
            item['author_link'] =''
            item['create_date'] = self.parseText(str=post.xpath('./tr/td[1]/text()').extract()[1])
            item['post'] = post_msg
            item['tag'] = 'multiple-sclerosis'
            item['topic'] = topic
            item['url'] = url
            #logging.info(post_msg)
            items.append(item)
        return items

