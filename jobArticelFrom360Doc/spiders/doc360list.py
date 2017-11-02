# -*- coding: utf-8 -*-
import scrapy
import json
from urllib.parse import urlparse#copy,urllib
from urllib.parse import parse_qs

class Doc360listSpider(scrapy.Spider):
    name = "doc360list"
    allowed_domains = ["http://www.360doc.com/ajax/ReadingRoom/getZCData.json?artNum=60&classId=3&subClassId=0&iIscream=0&iSort=1&nPage=1&nType=11"]
    #allowed_domains =['http://www.zheyibu.com']
    start_urls = []
    for i in range(1,101):
    	start_urls.append('http://www.360doc.com/ajax/ReadingRoom/getZCData.json?artNum=60&classId=3&subClassId=0&iIscream=0&iSort=1&nPage={0}&nType=11'.format(i))
    #start_urls = ['http://www.zheyibu.com/']
    #print(start_urls)

    def parse(self, response):
        filename='I:\\Scapy\\jobArticelFrom360Doc\\jobArticelFrom360Doc\\result\\doclist.json'
        url=urlparse(response.url)
        qs=parse_qs(url.query)
        #print(type(qs['nPage']))
        filename='I:\\Scapy\\jobArticelFrom360Doc\\jobArticelFrom360Doc\\result\\doclist_%s.json'%qs['nPage'][0]
        #print(response.url)
        with open(filename,'wb') as f:
        	responseContent=response.body
        	f.write(responseContent)
        	#responseObj=json.loads(responseContent)
        	#print(responseObj)
