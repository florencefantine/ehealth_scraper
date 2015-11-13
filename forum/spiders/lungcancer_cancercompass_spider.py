import scrapy
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.selector import Selector
from forum.items import PostItemsList
import re
import logging

# Spider for crawling Adidas website for shoes
class ForumsSpider(CrawlSpider):
    name = "lungcancer_cancercompass_spider"
    allowed_domains = ["www.cancercompass.com"]
    start_urls = [
        "http://www.cancercompass.com/message-board/cancers/lung-cancer/1,0,119,3.htm",
        "http://www.cancercompass.com/message-board/cancers/lung-cancer/non-small-cell/1,0,119,3,54.htm"
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                    restrict_xpaths='//a[@class="subLink"]',
                ), callback='parsePostsList'),
            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                    restrict_xpaths='//span[@id="MainContent_ContentPlaceHolder1_discussionList_dtpDis"]/a[last()]'
                ), follow=True),
        )

    # https://github.com/scrapy/dirbot/blob/master/dirbot/spiders/dmoz.py
    # https://github.com/scrapy/dirbot/blob/master/dirbot/pipelines.py
    def parsePostsList(self,response):
        sel = Selector(response)
        posts = sel.xpath('//div[@class="mbpost"]')
        items = []
        condition = "lung cancer"
        topic = response.xpath('//h1/text()').extract_first()
        url = response.url
        
        for post in posts:
            item = PostItemsList()
            item['author'] = post.xpath('.//div[@class="header"]/p/a/text()').extract_first()
            item['author_link'] = post.xpath('.//div[@class="header"]/p/a/@href').extract_first()
            item['condition'] = condition
            item['create_date'] = post.xpath('.//div[@class="header"]/p/text()').extract()[1].replace('on','').strip()
      
            item['post'] = re.sub('\s+',' '," ".join(post.xpath('.//div[@class="msgContent"]/p/text()').extract()).replace("\t","").replace("\n","").replace("\r","").replace(u'\xa0',''))
            item['tag']=''
            item['topic'] = topic
            item['url']=url
            logging.info(item.__str__)
            items.append(item)
        return items
