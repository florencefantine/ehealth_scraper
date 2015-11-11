import scrapy
from forum.items import PostItemsList
import time
from selenium import webdriver
from bs4 import BeautifulSoup
import re
import logging
class DailyStrength(scrapy.Spider):
	name = "chroniclymphocyticleukemia_dailystrength_spider"
	allowed_domains = ["dailystrength.org"]
	start_urls = [
		"http://www.dailystrength.org/c/Chronic-Lymphocytic-Leukemia-CLL/forum",
	]
	
	
	def cleanText(self, text):
		soup = BeautifulSoup(text, 'html.parser')
		text = soup.get_text();
		text = re.sub("( +|\n|\r|\t|\0|\x0b|\xa0|\xbb|\xab)+", ' ', text).strip()
		return text 


	def parse(self, response):
		driver = webdriver.PhantomJS()
		driver.get(response.url)
		links_xpath = "//table[@class='discussion_listing_main'][2]//tr/td[2]/a"
		links_lists = []
		for pageno in range(1,100):
			makeurl ="http://www.dailystrength.org/c/Chronic-Lymphocytic-Leukemia-CLL/forum/page-%s"%pageno
			driver.get(makeurl)
			time.sleep(3)
			get_links = driver.find_elements_by_xpath(links_xpath)
			logging.info("links:"+links_xpath)
			total_links = len(get_links)
			if total_links == 0:
				break
			for i in get_links:
				links_lists.append(i.get_attribute('href'))
		driver.close()
		for url in links_lists:
			logging.info("url:"+url)
			yield scrapy.Request(url,callback=self.get_sub_data)


	def get_sub_data(self,response):
		logging.info("get_sub_data")
		author_name_xpath = "//table[@class='discussion_topic']//p[@class='username']/a/text()"
		author_link_xpath = "//table[@class='discussion_topic']//p[@class='username']/a/@href"
		author_posted_xpath = "//table[@class='discussion_topic']//div/span[@class='graytext']/text()"
		author_all_text_xpath = "//table[@class='discussion_topic']//div[@class='discussion_text longtextfix485']/text()"

		author_name = response.xpath(author_name_xpath).extract()
		author_name = str(author_name[0])
		author_name = author_name.replace("\t","")

		author_name = author_name.replace(',',' ')
		author_link = response.xpath(author_link_xpath).extract()
		author_link  = author_link[0]
		author_link = "http://www.dailystrength.org%s"%author_link
		author_posted = response.xpath(author_posted_xpath).extract()
		author_posted = author_posted[0]
		author_posted = author_posted.replace(',','')
		author_posted = author_posted.replace('Posted on','')

		author_all_text = response.xpath(author_all_text_xpath).extract()
		author_all_text = str(author_all_text[0])
		author_all_text = author_all_text.replace(',','')
		author_all_text = author_all_text.replace('\t','')
		author_all_text = author_all_text.replace('  ','')
		author_all_text = author_all_text.replace('\n','')

		topic = response.xpath("//div[contains(@class,'discussion_topic_header_subject')]/text()").extract()[0]

		item = PostItemsList()

		item['author'] = author_name
		item['author_link'] = author_link
		item['condition']="chronic lymphocytic leukemia"
		item['create_date'] = author_posted
		item['post'] = author_all_text
		item['topic'] = topic
		item['url'] = response.url
		print(author_all_text)
		logging.info(item.__str__())
		yield item

