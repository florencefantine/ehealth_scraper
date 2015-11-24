# -*- coding: utf-8 -*-
import scrapy
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.selector import Selector
from forum.items import PostItemsList
import re
from bs4 import BeautifulSoup
import logging
import string
import dateparser
import time


# Spider for crawling Adidas website for shoes
class ForumsSpider(CrawlSpider):
    name = "all_medhelp_spider"
    allowed_domains = ["www.medhelp.org"]
    start_urls = [
        "http://www.medhelp.org/forums/Epilepsy/show/235",
        "http://www.medhelp.org/forums/Hepatitis-C/show/75",
        "http://www.medhelp.org/forums/Multiple-Sclerosis/show/41",
        "http://www.medhelp.org/forums/HIV---Prevention/show/117",
        "http://www.medhelp.org/forums/Leukemia--Lymphoma-/show/139",
        "http://www.medhelp.org/forums/Rheumatoid-Arthritis/show/377"
    ]

    rules = (
            Rule(LinkExtractor(
                    restrict_xpaths='//div[@class="fonts_resizable_subject subject_title "]/a',
                    canonicalize=False,
                ), callback='parsePostsList'),

            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                    restrict_xpaths='//div[@id="pagination_nav"]/a[@class="msg_next_page"]',
                    canonicalize=False,
                ), follow=True),
        )
    
    def getDate(self,date_str):
        # date_str="Fri Feb 12, 2010 1:54 pm"
        try:
            date = dateparser.parse(date_str)
            epoch = int(date.strftime('%s'))
            create_date = time.strftime("%Y-%m-%d'T'%H:%M%S%z",  time.gmtime(epoch))
            return create_date
        except Exception:
            #logging.error(">>>>>"+date_str)
            return date_str

    def cleanText(self,text, printableOnly =True):
        soup = BeautifulSoup(text,'html.parser')
        text = soup.get_text();
        text = re.sub("( +|\n|\r|\t|\0|\x0b|\xa0|\xbb|\xab)+",' ',text).strip()
        if printableOnly:
            return filter(lambda x: x in string.printable, text)
        return text

    def parsePostsList(self,response):
        sel = Selector(response)
        condition=" ".join(sel.xpath('//*[@id="community_header"]/div[1]/a[2]/text()').extract())
        posts = sel.xpath('//div[@class="post_message_container"]')
        items = []
        topic = response.xpath('//div[@class="question_title"]/text()').extract_first()
        url = response.url
        cnt =0
        for post in posts:
            item = PostItemsList()
            item['author'] = post.xpath('.//div[@class="post_byline"]/a/text()').extract_first()
            item['author_link'] = post.xpath('.//div[@class="post_byline"]/a/@href').extract_first()
            item['condition']=condition
            epoch_time = post.xpath("//span[contains(@class,'byline_date')]/@data-timestamp").extract()[0]
            # item['create_date']= time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(epoch_time)))
            item['create_date'] = self.getDate(epoch_time)
            msg = self.cleanText(" ".join(post.xpath('.//div[@class="post_message fonts_resizable"]/text()').extract()))
            item['post'] =msg
            item['topic'] = self.cleanText(topic)
            item['url']=url
            cnt+=1
            logging.info(msg)
            items.append(item)
        return items
