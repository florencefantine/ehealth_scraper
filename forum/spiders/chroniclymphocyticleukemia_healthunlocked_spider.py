# -*- coding: utf-8 -*-
import scrapy
from forum.items import PostItemsList
import time
import requests
import json
from selenium import webdriver
from bs4 import BeautifulSoup
import re
import string
import dateparser
import time
import logging

class HealthUnlocked(scrapy.Spider):
	name = "chroniclymphocyticleukemia_healthunlocked_spider"
	allowed_domains = ["healthunlocked.com"]
	start_urls = [
		"https://healthunlocked.com/cllsupport",
	]

	def cleanText(self, text):
		soup = BeautifulSoup(text, 'html.parser')
		text = soup.get_text();
		text = re.sub("( +|\n|\r|\t|\0|\x0b|\xa0|\xbb|\xab)+", ' ', text).strip()
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
            
	def parse(self, response):
		driver = webdriver.PhantomJS()
		# driver = webdriver.Firefox()
		driver.get(response.url)
		time.sleep(4)
		logging.info(response.body)
		view_all_xpath = "/a[contains(@href,'cllsupport/posts')]"
		# view_all_xpath='//*[@id="community-posts-panel"]/div/a'
		# view_all_xpath='//a[contains(@itemprop,"url")]'
		# driver.find_element_by_xpath(view_all_xpath).click()
		# jsres = driver.execute_script('return arguments[0].DataTable().data();', element)
		# print(jsres)
		# time.sleep(4)
		get_url = str(driver.current_url)
		get_url = get_url.split("/")
		get_url = get_url[3]
		logging.info(">>>> "+get_url)
		runable = True
		counter = 1
		driver.close()
		all_links_list = []
		while runable == True:
			site_api ="https://healthunlocked.com/api/posts?groupCode=%s&pageSize=20&pageNumber=%s"%(get_url,counter)
			get_json_data  = requests.get(site_api)
			response_json = json.loads(get_json_data.content)
			response_json = response_json['payload']
			response_json = response_json['posts']
			post_count = len(response_json)
			if post_count > 0:
				for ii in response_json:
					get_url_from_json = ii['postUrl']
					print get_url_from_json
					all_links_list.append(get_url_from_json)
			else:
				break
			counter = counter + 1
		for url in all_links_list:
			yield scrapy.Request(url,callback=self.get_sub_data)

	def get_sub_data(self,response):
		condition ="chronic lymphocytic leukemia"
		response_url = str(response.url)
		response_data_splitted = response_url.split("/")
		post_id = response_data_splitted[5]
		groupcode = response_data_splitted[3]

		link_to_get_actual_data = "https://healthunlocked.com/api/post/%s?id=%s&isDraft=false&groupCode=%s"%(post_id,post_id,groupcode)
		get_post_json = requests.get(link_to_get_actual_data)
		time.sleep(1)
		response_post_json = json.loads(get_post_json.content)
		response_post_json = response_post_json['payload']
		response_posts = response_post_json['post']

		author_username = response_posts['author']
		author_username = author_username['username']
		author_link = "https://healthunlocked.com/%s"%author_username

		posted_date = response_posts['dateCreated']
		author_all_text = response_posts['body']
		topic = response.css(".post-heading")

		item = PostItemsList()
		item['author'] = author_username
		item['author_link'] = author_link
		item['condition']=condition
		item['create_date'] = self.getDate(posted_date)
		item['post'] = author_all_text
		item['topic'] = topic
		item['url'] = response.url
		logging.info(author_all_text)
		yield item
