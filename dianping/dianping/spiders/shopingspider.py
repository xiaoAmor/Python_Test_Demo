# -*- coding: utf-8 -*-
import scrapy


class ShopingspiderSpider(scrapy.Spider):
    name = 'shopingspider'
    allowed_domains = ['www.dianping.com']
    start_urls = ['http://www.dianping.com/']

    def parse(self, response):
        print(response.status)
        pass
if __name__ == '__main__':
    from scrapy import cmdline
    cmdline.execute("scrapy crawl shopingspider".split())
