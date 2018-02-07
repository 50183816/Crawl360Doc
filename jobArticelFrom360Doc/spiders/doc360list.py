# -*- coding: utf-8 -*-
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
import pymongo
import datetime
class Doc360listSpider(scrapy.Spider):
    name = "doc360list"
    allowed_domains = ["360doc.com"]
    #allowed_domains =['http://www.zheyibu.com']
    start_urls = []
    custom_settings={
    #'MONGO_URI':'mongodb://192.168.1.163:2222/',
    'MONGO_URI':'mongodb://192.168.8.119:2222/',
    'MONGO_DATEBASE':'zheyibu'
    }
    for i in range(1,100):
    	start_urls.append('http://www.360doc.com/ajax/ReadingRoom/getZCData.json?artNum=60&classId=3&subClassId=0&iIscream=0&iSort=1&nPage={0}&nType=11'.format(i))
    #start_urls = ['http://www.zheyibu.com/']
    #print(start_urls)
    def __init__(self):
        self.mongo_uri = self.custom_settings.get('MONGO_URI')
        self.mongo_db = self.custom_settings.get('MONGO_DATEBASE','zheyibu')
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def checkNotExists(self,url):
        return self.db['JobDocList360'].find({'reviewurl':url}).count() == 0

    def parse(self, response):
        url=urlparse(response.url)
        qs=parse_qs(url.query)
        responseContent=response.text
        contentObj=json.loads(responseContent)
        for obj in contentObj[0]['data']:
            if self.checkNotExists(obj['StrUrl']):
                print(obj['StrUrl'])
                yield scrapy.Request(url=obj['StrUrl'],callback=self.parse_article)

    def parse_article(self,response):
        url = urlparse(response.url)
        path = url.path
        pathparts = path.split('/')
        usernameArticleId = pathparts[-1].split('.')[0]
        username = usernameArticleId.split('_')[0]
        articleId = usernameArticleId.split('_')[1]
        content = response.selector.xpath('//div[@id="articlecontent"]/table').extract_first()
        date = response.xpath('//div[contains(@class,"article_data_left")]/text()').extract_first().strip('\n')
        author = response.xpath('//div[contains(@class,"article_data_left")]/span/a/text()').extract_first()

        #reviewcount=response.selector.css('div[titwx::text]').extract()
        page = 1
        j = 1
        reviewUrl = 'http://webservice.360doc.com/GetArtInfo20130912NewV.ashx?GetReflection2=%s,%s,0,%s,%s,%d&jsoncallback=jsonp123'%(articleId,username,page,articleId,j)
        content = re.sub('href="([\s\S]*?)"','',content)
        content = re.sub('<img[\s\S]*?>','',content)
        content = re.sub('<script>[\s\S]*?</script>','',content)
        item = Jobarticelfrom360DocItem()
        item['reviewurl'] = response.url
        item['articleId'] = articleId
        item['content'] = content
        item['author'] = author
        item['date'] = datetime.datetime.strptime(date,'%Y-%m-%d') #要转到日期，否则Mongo里面字段会变成string ，影响排序
        item['title'] = response.selector.xpath('//h2[@id="titiletext"]/text()').extract_first()
        #item['image_urls'] = response.xpath('//div[@id="articlecontent"]//img/@src').extract()
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
        date = myresponse.selector.xpath('//div[contains(@class,"lf360")]/span[2]/text()').extract()
        review = myresponse.selector.xpath('//div[contains(@class,"pl_con")]/span/text()').extract()
        zhanlist = myresponse.xpath('//img[@src="http://pubimage.360doc.com/zhanyes.gif"]').extract()
        reviewIds = []
        for zhan in zhanlist:
            reviewIds.append(re.findall('onclick="zancai\(0,([\d]+?),',zhan)[0])
        zipedResult = zip(user,date,review,reviewIds)
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
            yield review


