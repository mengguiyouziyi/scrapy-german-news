# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CrawlerItem(scrapy.Item):
    url = scrapy.Field()
    visited = scrapy.Field()
    published = scrapy.Field()
    title = scrapy.Field()
    description = scrapy.Field()
    text = scrapy.Field()
    author = scrapy.Field()
    keywords = scrapy.Field()
