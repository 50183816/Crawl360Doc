# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Jobarticelfrom360DocItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    author = scrapy.Field()
    date = scrapy.Field()
    content = scrapy.Field()
    reviewurl = scrapy.Field()
    articleId = scrapy.Field()

#
class ArticleReviewItem(scrapy.Item):
	user = scrapy.Field()
	date = scrapy.Field()
	review = scrapy.Field()
	articleId = scrapy.Field()
	reviewId = scrapy.Field()