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

fetch("http://www.ldonline.org/xarbb/topic/33120")
sel = Selector(response)
posts = response.xpath('//table//tr')[1:-1:2]
post = posts[0]

def getDate(date_str):
        # date_str="Fri Feb 12, 2010 1:54 pm"
        try:
            date = dateparser.parse(date_str)
            epoch = int(date.strftime('%s'))
            create_date = time.strftime("%Y-%m-%d'T'%H:%M%S%z",  time.gmtime(epoch))
            return create_date
        except Exception:
            logging.error(">>>>>"+date_str)
            return date_str

def cleanText(text,printableOnly = True):
    soup = BeautifulSoup(text,'html.parser')
    text = soup.get_text();
    text = re.sub("( +|\n|\r|\t|\0|\x0b|\xa0|\xbb|\xab)+",' ',text).strip()
    if printableOnly:
        return filter(lambda x: x in string.printable, text)
    return text

create_date = getDate( cleanText( re.sub(r'(Posted:|\[|])','', ''.join(post.xpath('.//td[@class="tableRowHeading"]//text()').extract()) ).replace("Ignore","") ))


'''

    def cleanText(self,text,printableOnly=True):
        soup = BeautifulSoup(text,'html.parser')
        text = soup.get_text();
        text = re.sub("(-+| +|\n|\r|\t|\0|\x0b|\xa0|\xbb|\xab)+",' ',text).strip()
        if(printableOnly):
            return filter(lambda x: x in string.printable, text)
        return text 

    def getDate(self,date_str):
        # date_str="Fri Feb 12, 2010 1:54 pm"
        try:
            date = dateparser.parse(date_str)
            epoch = int(date.strftime('%s'))
            create_date = time.strftime("%Y-%m-%d'T'%H:%M%S%z",  time.gmtime(epoch))
            return create_date
        except Exception:
            logging.error(">>>>>"+date_str)
            return date_str
     
'''