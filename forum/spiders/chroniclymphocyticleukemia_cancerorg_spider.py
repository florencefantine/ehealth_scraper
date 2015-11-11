import scrapy
from forum.items import PostItemsList
import re
from bs4 import BeautifulSoup

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

	def get_all_data(self,response):
		author_name_xpath = "//table[@class='node node-forum']//div[@class='author']/text()"
		submitted_date_xpath = "//table[@class='node node-forum']//div[@class='submitted']/text()"
		all_text_data_xpath = "//table[@class='node node-forum']//div[@class='content']/p/text()"

		item = PostItemsList()
		item['author'] = response.xpath(author_name_xpath).extract()[0]
		item['author_link'] = ''
		item['condition']="chronic lymphocytic leukemia"
		item['create_date'] = response.xpath(submitted_date_xpath).extract()[0]
		item['url'] = response.url
		item['post'] = self.cleanText(response.xpath(all_text_data_xpath).extract()[0])
		yield item