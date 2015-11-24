## how to use


### make sure you have scrapy installed these:
	pip install scrapyd
	pip install beautifulsoup4
	pip install lxml
	pip install chardet
	pip install cssselect
	pip install dateparser

### play around with scrapy to understand how it does css or xpath selection 

It's the same as beautiful soup or jsoup, or lxml, or other html parsers

	cd ehealth;
	scrapy shell http://ehealthforum.com/health/epilepsy.html
	response.xpath("//h1")
	response.css(".fp_h2")
	ctrl-Z to exit the shell

### run a crawler

	scrapy crawl epilepsy_ehealthforums_spider

you see that items are being logged


### explaination of the hepc_hepmag_spider
for this spider, there are 2 rules
- rule 1, use css selectors to get the links of all the topics
- rule 2, use css selectors to get the links of the paginations, and ask it to follow, but exclude following into links for user profiles

####Then there is a parse method
in the parse method, the spider has landed in each individual topic's page, and is now picking out each of the posts, and putting them into the item object which is defined in items.py
Those are examples of good to have fields that the Item should have.



## For more information
see http://doc.scrapy.org/en/latest/topics/api.html
and https://github.com/Axiologue/ShoeScraper


