import scrapy
from forum.items import PostItemsList
import re
from bs4 import BeautifulSoup
import logging

class CancerCompass(scrapy.Spider):
	name = "chroniclymphocyticleukemia_cancercompass_spider"
	allowed_domains = ["cancercompass.com"]
	start_urls = [
		"http://www.cancercompass.com/message-board/cancers/leukemia/leukemia-(cll)/1,0,119,7,50.htm",
	]

	def parse(self, response):
		for href in response.xpath("//a[@class='subLink']/@href"):
			url = response.urljoin(href.extract())
			print url
			yield scrapy.Request(url, callback=self.get_all_data)
		next_page = response.xpath("//a[text()='Next']/@href")
		if next_page:
			url = response.urljoin(next_page[0].extract())
			yield scrapy.Request(url,callback=self.parse)

	def cleanText(self,text):
		soup = BeautifulSoup(text,'html.parser')
		text = soup.get_text();
		text = re.sub("( +|\n|\r|\t|\0|\x0b|\xa0|\xbb|\xab)+",' ',text).strip()
		return text 
	
	def get_all_data(self, response):
		author_name_xpath  = "//div[@class='mbpost'][1]//div[@class='author']/p/a/span/text()"
		author_link_xpath  = "//div[@class='mbpost'][1]//div[@class='author']/p/a/@href"
		publish_date_xpath = "//div[@class='mbpost'][1]//div[@class='message']/div[@class='header']/p/text()" #remove "By" and "on"
		post_text_xpath    = "//div[@class='mbpost'][1]//div[@class='message']/div[@class='msgContent']/p/text()" 

		author_name = response.xpath(author_name_xpath).extract()[0]

		author_link = response.xpath(author_link_xpath).extract()
		try:author_link  = "http://www.cancercompass.com%s"%(author_link[0])
		except:author_link  = "http://www.cancercompass.com%s"%(author_link)
		publish_date = response.xpath(publish_date_xpath).extract()
		publish_date =  str(publish_date[1])
		publish_date = publish_date.replace('on','')

		topic=response.xpath('//div[contains(@class,"contentText")]/h1/text()').extract()[0]
		
		post_text = " ".join(response.xpath(post_text_xpath).extract())
		if post_text == '':
			post_text = " ".join(response.xpath("//div[@class='mbpost'][1]//div[@class='msgContent']/text()").extract())
			logging.info(post_text)

		item = PostItemsList()

		item['author'] = response.xpath(author_name_xpath).extract()
		item['author_link'] = author_link
		item['condition']="chronic lymphocytic leukemia"
		item['create_date'] = publish_date
		item['post'] = post_text
		item['topic'] = self.cleanText(topic)
		item['url'] = response.url
		yield item
		