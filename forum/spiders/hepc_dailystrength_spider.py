import scrapy
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.selector import Selector
from forum.items import PostItemsList
import re
import logging

class ForumsSpider(CrawlSpider):
    name = "hepc_dailystrength_spider"
    allowed_domains = ["www.dailystrength.org"]
    start_urls = [
        "http://www.dailystrength.org/c/Hepatitis-C/forum",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                    restrict_xpaths='//tr[contains(@class, "sectiontableentry")]//a[@class="strong"]', 
                ), callback='parsePostsList'),
            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                    restrict_xpaths='//table[@class="davetest"]/tr[3]//a[text(), "next"]'
                ), follow=True),
        )

    def parsePostsList(self,response):
        sel = Selector(response)
        posts = sel.xpath('//table[@class="reply_table"]/tr')
        items = []
        condition="hep c"
        topic = response.xpath('//div[@class="discussion_topic_header_subject"]/text()').extract_first()
        url = response.url

        item = PostItemsList()
        item['author'] = response.xpath('.//p[@class="username"]/a/text()').extract_first()
        item['author_link'] = response.xpath('.//p[@class="username"]/a/@href').extract_first()
        item['condition'] = condition
        item['create_date'] = response.xpath('.//div[contains(@class, "discussion_text")]/span/text()').extract_first().replace(u'Posted on','').strip()  
        item['post'] = re.sub('\s+',' '," ".join(response.xpath('.//div[contains(@class, "discussion_text")]/text()').extract()).replace("\t","").replace("\n","").replace("\r","").replace(u'\xa0',''))
        item['tag']='epilepsy'
        item['topic'] = topic.strip()
        item['url']=url
        logging.info(item.__str__)
        items.append(item)
        
        for post in posts:
            item = PostItemsList()
            item['author'] = post.xpath('.//p[@class="username"]/a/text()').extract_first()
            if item['author']:
                item['author'] = item['author'].strip()
                item['author_link'] = post.xpath('.//p[@class="username"]/a/@href').extract_first()
                item['condition'] = condition
                item['create_date'] = post.xpath('.//span[@class="graytext"][2]/text()').extract_first().strip()
          
                item['post'] = re.sub('\s+',' '," ".join(post.xpath('.//div[contains(@class, "discussion_text")]/text()').extract()).replace("\t","").replace("\n","").replace("\r","").replace(u'\xa0',''))
                item['tag']='epilepsy'
                item['topic'] = topic.strip()
                item['url']=url
                logging.info(item.__str__)
                items.append(item)
        return items
