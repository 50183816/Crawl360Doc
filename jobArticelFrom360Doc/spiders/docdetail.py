import scrapy
import json
import os
from urllib.parse import urlparse#copy,urllib
from urllib.parse import parse_qs
from scrapy.selector import Selector
from scrapy.http import HtmlResponse
from jobArticelFrom360Doc.items import Jobarticelfrom360DocItem
from jobArticelFrom360Doc.items import ArticleReviewItem
import re
#from w3lib.html import remove_tags
class DocDetailCrawlerSpider(scrapy.Spider):
	name='DocDetailCrawler'
	allowed_domains=['360doc.com']
	custom_settings={
	'MONGO_URI':'mongodb://192.168.8.119:2222/',
	'MONGO_DATEBASE':'zheyibu'
	}
	#self.LoadUrl()
	start_urls=[]
	def __init__(self):
		self.start_urls = self.LoadUrl(self.start_urls)
		#print(self.start_urls)


	def LoadUrl(self,start_urls):
		start_urls=[]
		for i in range(1,2):
			filename = 'I:\\Scapy\\result\\doclist_%d.json'%i
			if not os.path.exists(filename):
				continue
			#print(filename)
			urlFile=open(filename,'r',encoding='UTF-8')
			content=urlFile.read()
			contentObj=json.loads(content)
			for obj in contentObj[0]['data']:
				start_urls.append(obj['StrUrl'])
				#print(obj['StrUrl'])
				#break
				#pass
			
			urlFile.close()
		return start_urls

	def parse(self,response):
		#print(response.url)
		url = urlparse(response.url)
		path = url.path
		pathparts = path.split('/')
		usernameArticleId = pathparts[-1].split('.')[0]
		username = usernameArticleId.split('_')[0]
		articleId = usernameArticleId.split('_')[1]
		#print(pathparts[-1].split('.')[0])
		#filename = 'I:\\Scapy\\jobArticelFrom360Doc\\jobArticelFrom360Doc\\docresult\\doc_%s.html'%pathparts[-1].split('.')[0]
		#body=response.body
		content = response.selector.xpath('//div[@id="articlecontent"]/table').extract_first()
		#style="[\s\S^"]*?"|<img[\s\S^>]*?>|<script>[\s\S]*?</script>
		#remove_tags(content)
		#if not content:
			#content = response.selector.xpath('//div[@id="word_inside"]').extract_first()
		date = response.xpath('//div[contains(@class,"article_data_left")]/text()').extract_first().strip('\n')
		author = response.xpath('//div[contains(@class,"article_data_left")]/span/a/text()').extract_first()

		#reviewcount=response.selector.css('div[titwx::text]').extract()
		#print(content)
		page = 1
		j = 1
		reviewUrl = 'http://webservice.360doc.com/GetArtInfo20130912NewV.ashx?GetReflection2=%s,%s,0,%s,%s,%d&jsoncallback=jsonp123'%(articleId,username,page,articleId,j)
		item = Jobarticelfrom360DocItem()
		item['reviewurl'] = response.url
		item['articleId'] = articleId
		item['content'] = content
		item['author'] = author
		item['date'] = date
		item['title'] = response.selector.xpath('//h2[@id="titiletext"]/text()').extract_first()
		item['image_urls'] = response.xpath('//div[@id="articlecontent"]//img/@src').extract()
		yield item
		# item={
		# title:'',
		# author:'',
		# date:'',
		# content:'',
		# reviewurl:'http://webservice.360doc.com/GetArtInfo20130912NewV.ashx?GetReflection2=%s,%s,0,%s,%s,%d&jsoncallback=jsonp123'%(articleId,username,page,articleId,j)
		# }
		#yield {'request':scrapy.Request(url=item['reviewurl'],callback=self.parse_review,meta={'page':1,'articleId':articleId}),'DocItem':item}
		yield scrapy.Request(url=reviewUrl,callback=self.parse_review,meta={'page':1,'articleId':articleId})

	def parse_review(self,response):
		jsonp = response.body
		#print(response.meta.get('page'))
		jj = jsonp[12:-12]
		myresponse = HtmlResponse(url='jj',body=jj,encoding='utf-8')
		user = myresponse.selector.xpath('//span[contains(@class,"mzbodl")]/a/text()').extract()
		#print(user)
		date = myresponse.selector.xpath('//div[contains(@class,"lf360")]/span[2]/text()').extract()
		#print(date)
		review = myresponse.selector.xpath('//div[contains(@class,"pl_con")]/span/text()').extract()
		#print(review)
		zhanlist = myresponse.xpath('//img[@src="http://pubimage.360doc.com/zhanyes.gif"]').extract()
		reviewIds = []
		for zhan in zhanlist:
			reviewIds.append(re.findall('onclick="zancai\(0,([\d]+?),',zhan)[0])
		zipedResult = zip(user,date,review,reviewIds)
		#print(list(zipedResult))
		for item in list(zipedResult):
			review = ArticleReviewItem()
			review['user'] = item[0]
			review['date'] = item[1]
			review['review'] = item[2]
			review['articleId'] = response.meta.get('articleId')
			review['reviewId'] = item[3]
			# review={
			# 'user':item[0],
			# 'date':item[1],
			# 'review':item[2],
			# 'articleId':response.meta.get('articleId')
			# }
			#print(review['user'])
			yield review









