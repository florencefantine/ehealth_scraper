# -*- coding: utf-8 -*-
import scrapy
import hashlib
from forum.items import PostItemsList
import time
from bs4 import BeautifulSoup
import re
import string
import dateparser
import time

class LymphomasSpider(scrapy.Spider):
    name = "lymphoma_lymphomasorg_spider"
    allowed_domains = ["lymphomas.org.uk"]
    start_urls = [
        "http://www.lymphomas.org.uk/forum",
    ]

    def getDate(self,date_str):
        try:
            date = dateparser.parse(date_str)
            epoch = int(date.strftime('%s'))
            create_date = time.strftime("%Y-%m-%d'T'%H:%M%S%z",  time.gmtime(epoch))
            return create_date
        except Exception:
            #logging.error(">>>>>"+date_str)
            return date_str

    def cleanText(self,text,printableOnly=True):
        soup = BeautifulSoup(text,'html.parser')
        text = soup.get_text();
        text = re.sub("(-+| +|\n|\r|\t|\0|\x0b|\xa0|\xbb|\xab)+",' ',text).strip()
        if(printableOnly):
            return filter(lambda x: x in string.printable, text)
        return text 


    def parse(self,response):
        links_xpath = "//div[@class='forum-name']/a/@href"
        for href in response.xpath(links_xpath):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.get_all_data)

    def get_all_data(self,response):
        links_xpath_sub = "//span[@class='forum-topic-title']/../@href"
        for href in response.xpath(links_xpath_sub):
            url = response.urljoin(href.extract())
            print url
            yield scrapy.Request(url, callback=self.get_main_data)

        next_page_xpath = "//li[@class='pager-next']/a/@href"
        next_page = response.xpath(next_page_xpath)
        if next_page:
            url = response.urljoin(next_page[0].extract())
            yield scrapy.Request(url,callback=self.parse)

    def get_main_data(self,response):
        author_name_xpath = "//div[@id='content']/div[3]//span[@class='username']/text()"
        author_link_xpath = "//div[@id='content']/div[3]//span[@class='username']/@about"
        author_date_posted_xpath = "//div[@id='content']/div[3]/div[1]/div[1]/span/text()"
        author_text_xpath = "//div[@id='content']/div[3]//div[@class='field-items']//p/text()"
        condition = "lymphoma"
        author_link = "https://www.lymphomas.org.uk%s"%response.xpath(author_link_xpath).extract()[0]
        topic = response.xpath('//*[@id="content"]/h1/text()').extract()[0]

        item = PostItemsList()
        item['author'] = response.xpath(author_name_xpath).extract()[0]
        item['author_link'] = author_link
        item['condition']=condition
        item['create_date'] = self.getDate(response.xpath(author_date_posted_xpath).extract()[0])
        item['domain'] = "".join(self.allowed_domains)
        item['post'] = self.cleanText(" ".join(response.xpath(author_text_xpath).extract()))
        item['topic'] = topic
        item['url'] = response.url
        yield item
