# -*- coding: utf-8 -*-

# Scrapy settings for forum project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'forum'

SPIDER_MODULES = ['forum.spiders']
NEWSPIDER_MODULE = 'forum.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'forum (+http://www.yourdomain.com)'
USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36'

ITEM_PIPELINES = {
#     'forum.pipelines.DuplicatesLinksPipeline': 300,
    # 'forum.fluentd_pipelines.FluentdPipeline': 400
}

COOKIES_ENABLED = True
COOKIES_DEBUG = True

DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.redirect.RedirectMiddleware':543,
#     'scrapy_crawlera.CrawleraMiddleware': 600
}
REDIRECT_ENABLED=True

ROBOTSTXT_OBEY=False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
HTTPCACHE_ENABLED=True
#HTTPCACHE_EXPIRATION_SECS=0
HTTPCACHE_DIR='httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES=[]
HTTPCACHE_STORAGE='scrapy.extensions.httpcache.FilesystemCacheStorage'

FLUENTD_URI='localhost'
FLUENTD_PORT=24224
FLUENTD_CHANNEL='FM'