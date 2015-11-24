# -*- coding: utf-8 -*-
import scrapy
import hashlib
from forum.items import PostItemsList
import re
from bs4 import BeautifulSoup
import string
import dateparser
import time

class CancerCompass(scrapy.Spider):
	name = "chroniclymphocyticleukemia_cancerorg_spider"
	allowed_domains = ["csn.cancer.org"]
	start_urls = [
		"http://csn.cancer.org/forum/135",
	]

	def cleanText(self,text):
		soup = BeautifulSoup(text,'html.parser')
		text = soup.get_text();
		text = re.sub("( +|\n|\r|\t|\0|\x0b|\xa0|\xbb|\xab)+",' ',text).strip()
		return text 
	
	def parse(self, response):
		links_path = "//td[@class='title']//a/@href"

		for href in response.xpath(links_path):
			url = response.urljoin(href.extract())
			print url
			yield scrapy.Request(url, callback=self.get_all_data)
		next_page_xpath ="//li[@class='pager-next']/a/@href"
		next_page = response.xpath(next_page_xpath)
		if next_page:
			url = response.urljoin(next_page[0].extract())
			yield scrapy.Request(url,callback=self.parse)


	def getDate(self,date_str):
		try:
		    date = dateparser.parse(date_str)
		    epoch = int(date.strftime('%s'))
		    create_date = time.strftime("%Y-%m-%d'T'%H:%M%S%z",  time.gmtime(epoch))
		    return create_date
		except Exception:
		    #logging.error(">>>>>"+date_str)
		    return date_str
            
	def get_all_data(self,response):
		author_name_xpath = "//table[@class='node node-forum']//div[@class='author']/text()"
		submitted_date_xpath = "//table[@class='node node-forum']//div[@class='submitted']/text()"
		all_text_data_xpath = "//table[@class='node node-forum']//div[@class='content']/p/text()"
		condition = "chronic lymphocytic leukemia"
		subject = response.xpath(
		            '//div[@class="left-corner"]/h2/text()'
		        ).extract()[0]
		item = PostItemsList()
		item['author'] = response.xpath(author_name_xpath).extract()[0]
		item['author_link'] = ''
		item['condition']=condition
		item['create_date'] = self.getDate(response.xpath(submitted_date_xpath).extract()[0])
		item['domain'] = "".join(self.allowed_domains)
		item['post'] = self.cleanText(response.xpath(all_text_data_xpath).extract()[0])
		item['topic'] = subject
		item['url'] = response.url
		yield item
