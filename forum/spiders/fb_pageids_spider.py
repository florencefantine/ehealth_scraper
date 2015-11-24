#!/usr/bin/env python
from __future__ import print_function
import scrapy
from scrapy.contrib.spiders import CrawlSpider, Rule, Spider, Request
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.selector import Selector
from forum.items import PostItemsList
import re
import logging

from selenium import webdriver
from bs4 import BeautifulSoup
from argparse import ArgumentParser
from time import sleep
import getpass
import sys
import logging


class ForumsSpider(Spider):
    name = "fb_pageids_spider"
    allowed_domains = ["facebook.com"]
    start_urls = [
        "http://www.example.com",   #just a dummy start_url
    ]
    
    login_url = "https://www.facebook.com/login/"
    
    #use proxy to login, if not use, comment it out
    #service_args = [
    #    '--proxy=127.0.0.1:8087',
    #    '--proxy-type=https',
    #    ]

    #driver = webdriver.PhantomJS(service_args=service_args)
    driver = webdriver.PhantomJS()
    
    keyword="epilepsy"
    wait = 1

    ##***********************************************
    # put your email and password here
    email = ''
    password = ''
    ##***********************************************

    def login(self):
        """
        Log in to Facebook, set profile name
        :return: Null
        """
        self.driver.get(self.login_url)
        email_element = self.driver.find_element_by_id('email')
        email_element.send_keys(self.email)
        password_element = self.driver.find_element_by_id('pass')
        password_element.send_keys(self.password)
        password_element.submit()

        soup = BeautifulSoup(self.driver.page_source)
        profile_link = soup.find('a', {'title': 'Profile'})
        self.profile_name = profile_link.get('href')[25:]    # link appears as http://www.facebook.com/PROFILE
        print(self.profile_name)


    def search(self, keyword):
        self.driver.get('https://www.facebook.com/search/str/'+keyword+'/keywords_pages')
        sleep(self.wait)
        
    def scroll_down(self):
        """
        Executes JS to scroll down on page.
        Use if having trouble seeing elements
        :return:
        """
        self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        sleep(self.wait)


    def _is_it_end_of_page(self):
        return self.driver.find_element_by_xpath(".//*[@id='browse_end_of_results_footer']/div/div/div")


    def parse(self,response):
        #we do not use response
        self.login()
        self.search(self.keyword)

        self.parsePageID(self.driver.page_source)
        
        isEnd = False
        pageids = []

        while not isEnd:
            try:
                #You should comment out the following one line
                #self._is_it_end_of_page()
                for id in self.parsePageID(self.driver.page_source):
                    if id in pageids:
                        isEnd = True
                        break
                    pageids.append(id)                
            except:
                #You should comment out the following one line
                #self.scroll_down()
                pass
                
        self.driver.close()
        
        item = PostItemsList()
        item['topic'] = pageids
        
        return item
        

    def parsePageID(self, page_source):
        sel = Selector(text=self.driver.page_source)
        infos = sel.xpath('//*[@class="_gll"]/a/@href').extract()
        
        pageids = []
        
        for info in infos:
            pageid = info.split("/").pop(-2)
            pageids.append(pageid)
            print(pageid)
            
        return pageids
