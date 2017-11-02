# -*- coding: utf-8 -*-
import scrapy


class ExampleSpider(scrapy.Spider):
    name = "example"
    allowed_domains = ["www.zheyibu.com"]
    start_urls = ['http://www.zheyibu.com/']

    def parse(self, response):
        pass
