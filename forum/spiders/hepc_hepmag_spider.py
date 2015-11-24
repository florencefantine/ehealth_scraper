# -*- coding: utf-8 -*-
import scrapy
import hashlib
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.selector import Selector
from forum.items import PostItemsList
import logging
import lxml.html
from lxml.etree import ParserError
from lxml.cssselect import CSSSelector
import re
from bs4 import BeautifulSoup
import urlparse
import urllib
import string
import dateparser
import time


## LOGGING to file
#import logging
#from scrapy.log import ScrapyFileLogObserver

#logfile = open('testlog.log', 'w')
#log_observer = ScrapyFileLogObserver(logfile, level=logging.DEBUG)
#log_observer.start()


class ForumsSpider(CrawlSpider):
    name = "hepc_hepmag_spider"
    _allowed_domain = {"forums.hepmag.com" }
    start_urls = [
        "http://forums.hepmag.com/index.php?board=31.0"
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                    restrict_xpaths='//span[contains(@id,"msg_")]/a',
                    canonicalize=True,
                ), callback='parsePostsList'),
            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                    restrict_xpaths='//a[@class="navPages"]',
                    canonicalize=True,
                    deny=(r'profile',)
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

    def urlRemove(self,url,keyToFind):
        url_parts = list(urlparse.urlparse(url))
        query = dict(urlparse.parse_qsl(url_parts[4]))
        
        for q in query.keys():
            if q == keyToFind:
                query.pop(q,None)
        url_parts[4] = urllib.urlencode(query)
        return urlparse.urlunparse(url_parts)
    

    def cleanText(self,text,printableOnly=True):
        soup = BeautifulSoup(text,'html.parser')
        text = soup.get_text();
        text = re.sub("(-+| +|\n|\r|\t|\0|\x0b|\xa0|\xbb|\xab)+",' ',text).strip()
        if(printableOnly):
            return filter(lambda x: x in string.printable, text)
        return text 
    
    # https://github.com/scrapy/dirbot/blob/master/dirbot/spiders/dmoz.py
    # https://github.com/scrapy/dirbot/blob/master/dirbot/pipelines.py
    def parsePostsList(self,response):
        condition ="hepatitis-c"
        try:
            document = lxml.html.fromstring(response.body)
            document.make_links_absolute(base_url=response.url, resolve_base_href=True)
        except ParserError:
            return
        items =[]
        postWrappers = CSSSelector('.post_wrapper')(document)
        for postWrapper in postWrappers:
            post = PostItemsList()
            keyinfo = postWrapper.cssselect(".keyinfo")[0]
            poster = postWrapper.cssselect(".poster")[0]
            post['author'] = poster.xpath("./h4/a/text()")[0]
            post['author_link'] = poster.xpath("./h4/a/@href")[0]
            post['condition'] = condition
            create_date = self.cleanText(" ".join(keyinfo.cssselect('.smalltext')[0].xpath("text()")))
            post['create_date'] = self.getDate(create_date)
            item['domain'] = "".join(self.allowed_domains)
            post['topic'] = keyinfo.cssselect('h5')[0].xpath("./a/text()")[0]
            post['post'] = self.cleanText(" ".join(postWrapper.cssselect(".post")[0].xpath("./div/text()")))
            post['url'] = self.urlRemove(response.url,"PHPSESSID")
            items.append(post)
        return items
        
