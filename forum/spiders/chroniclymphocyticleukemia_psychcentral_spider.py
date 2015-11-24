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

class PsychCentral(scrapy.Spider):
	name = "chroniclymphocyticleukemia_psychcentral_spider"
	allowed_domains = ["psychcentral.com"]
	start_urls = [
		"http://forums.psychcentral.com/health-support/",
	]

	def parse(self, response):
		links_xpath = "//table//a[@style='font-weight:bold']/@href"
		for href in response.xpath(links_xpath):
			url = response.urljoin(href.extract())
			print url
			yield scrapy.Request(url, callback=self.get_all_data)
		next_page_xpath = "//a[text()='>']/@href"
		next_page = response.xpath(next_page_xpath)
		if next_page:
			url = response.urljoin(next_page[0].extract())
			yield scrapy.Request(url,callback=self.parse)

	def cleanText(self,text):
		soup = BeautifulSoup(text,'html.parser')
		text = soup.get_text();
		text = re.sub("( +|\n|\r|\t|\0|\x0b|\xa0|\xbb|\xab)+",' ',text).strip()
		return text 


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
		post_id = response.xpath('//td[contains(@class,"alt1")]/@id').extract_first().split("_")[-1]
		date = [self.cleanText(x) for x in response.xpath('//a[contains(@name,"post'+post_id+'")]/../text()').extract()]
		date = " ".join([x for x in date if x!=''])
		post_text = response.css('.alt1').xpath('div[2]/text()').extract()
		try:
			post_text = str(post_text[1])
			post_text = post_text.replace('\r','')
			post_text = post_text.replace('\n','')
			post_text = post_text.replace('\t','')
		except:pass
		# //*[@id="post4713098"]/tbody/tr[1]/td[1]/text()
		#date = " ".join(response.xpath("//tr//td[1]/text()").extract())
		# date = " ".join(response.css('.thead').xpath('text()').extract())
		# date = self.cleanText(date)
		condition = "chronic lymphocytic leukemia"
		topic = self.cleanText(response.xpath(
				'//td[contains(@class,"navbar")]/strong/text()'
				).extract()[0])

		item = PostItemsList()
		item['author'] = response.css('.bigusername').xpath('text()').extract_first()
		item['author_link'] = response.css('.bigusername').xpath('@href').extract_first()
		item['condition']=condition
		item['create_date'] = self.getDate(date)
		item['domain'] = "".join(self.allowed_domains)
		item['post'] = self.cleanText(post_text)
		item['topic'] = topic
		item['url'] = response.url
		yield item


