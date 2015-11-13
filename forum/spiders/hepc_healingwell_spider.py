import scrapy
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.selector import Selector
from forum.items import PostItemsList
import re
import logging

class ForumsSpider(CrawlSpider):
    name = "hepc_healingwell_spider"
    allowed_domains = ["www.healingwell.com"]
    start_urls = [
        "http://www.healingwell.com/community/default.aspx?f=25",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                    restrict_xpaths='//td[@class="msgTopicAnnounce TopicTitle"]/a', 
                ), callback='parsePostsList'),
            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                    restrict_xpaths='//td[@class="msgSm" and @align="right"]/b/strong/following-sibling::a[1]'
                ), follow=True),
        )

    def parsePostsList(self,response):
        sel = Selector(response)
        posts = sel.xpath('//table[@class="PostBox"]')
        items = []
        topic = response.xpath('//h1/text()').extract_first()
        url = response.url
        
        for post in posts:
            item = PostItemsList()
            item['author'] = post.xpath('.//td[@class="msgUser"]/a[2]/text()').extract_first()
            if item['author']:
                item['author_link'] = post.xpath('.//td[@class="msgUser"]/a[2]/@href').extract_first()
                item['create_date'] = post.xpath('.//td[@class="msgThreadInfo PostThreadInfo"]/text()').extract_first().replace(u'\xa0','').replace(u'Posted','').strip()
          
                item['post'] = re.sub('\s+',' '," ".join(post.xpath('.//div[@class="PostMessageBody"]/text()').extract()).replace("\t","").replace("\n","").replace("\r","").replace(u'\xa0',''))
                item['tag']='epilepsy'
                item['topic'] = topic.strip()
                item['url']=url
                logging.info(item.__str__)
                items.append(item)
        return items
