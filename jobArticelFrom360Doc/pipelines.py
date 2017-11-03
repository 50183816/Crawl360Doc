# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline
from scrapy.http import Request
class Jobarticelfrom360DocPipeline(object):
	def __init__(self,mongo_uri,mongo_db):
		self.mongo_uri = mongo_uri
		self.mongo_db = mongo_db
	@classmethod
	def from_crawler(cls,crawler):
		return cls(mongo_uri=crawler.settings.get('MONGO_URI'),mongo_db=crawler.settings.get('MONGO_DATEBASE','zheyibu'))

	def open_spider(self,spider):
		self.client = pymongo.MongoClient(self.mongo_uri)
		self.db = self.client[self.mongo_db]

	def close_spider(self,spider):
		self.client.close()

	def process_item(self, item, spider):
		if item.get('user'):
			#return item
			if self.db['360DocReview'].find({'reviewId':item['reviewId']}).count() == 0:
				self.db['360DocReview'].insert(dict(item))
		if item.get('reviewurl') and item.get('content'):
			if self.db['360DocList'].find({'articleId':item.get('articleId')}).count() == 0:
				originalImageUrl = item['image_urls']
				localImageUrl = item['image_paths']
				zippedImage = zip(originalImageUrl,localImageUrl)
				for image in list(zippedImage):
					item['content'] = item['content'].replace(image[0],'http://static.zheyibu.com/careerdoc/images/'+image[1])
				self.db['360DocList'].insert(dict(item))
			#return item
		else:
			raise DropItem('Empty item')

class MyImagePipeline(ImagesPipeline):
	def get_media_requests(self,item,info):
		if(item.get('image_urls')):
			for image_url in item['image_urls']:
				yield Request(image_url)
		else:
			return item
	def item_completed(Self,results,item,info):
		if(not item.get('image_urls')):
			return item
		image_paths = [x['path'] for ok, x in results if ok]
		if not image_paths:
			raise DropItem('Item contains no images')
		item['image_paths'] = image_paths
		return item