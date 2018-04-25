#!/usr/bin/python
#coding:utf-8
'''
Created on 2018��4��24��

@author: Administrator
'''
# URL管理器类
#HTML 下载器
#HTML 解析器
#存储器
#调度器
import requests
from bs4 import BeautifulSoup

import re
import urlparse
import codecs
import json
import io
from _codecs import encode
import copy

# URL管理器类 
"""
是否有代取的url
 未爬取集合 已爬取集合
 未爬取集合数量  已爬取集合数量
 添加未爬取的单个  多个
"""
global get_message_num

#使用集合存储  集合不能存在相同的元素
class UrlManger(object):
    def __init__(self):
        self.new_urls=set()#未爬取的url集合
        self.old_urls=set()#已经爬取url集合
        #未爬取url数量
    def new_url_size(self):
        return len(self.new_urls)
    #已经爬取url数量
    def old_url_size(self):
        return len(self.old_urls)
    #判断是否有新未爬取url
    def has_new_url(self):
        if self.new_url_size()==0:
            return 0;
        
        if self.new_url_size()!=0:
            return self.new_url_size()
        #取一个url
    def get_new_url(self):
        #未爬取集合中取出一个 同时添加到已爬取集合
        new_url=self.new_urls.pop()
        self.old_urls.add(new_url)
        return new_url
    #添加一个未爬取的url 需要判断
    def add_new_url(self,url):
        if url is None:
            return
        #过滤相同的url和已经爬取的url
        if url not in self.new_urls and url not in self.old_urls:
            self.new_urls.add(url)
    def add_new_urls(self,urls):
        if urls is None and len(urls)==0:
            return
        for url in urls:
            self.add_new_url(url)
 #HTML下载器       
class HtmlDownloader(object):
    def download(self,url):
        if url is None:
            return
        user_agent ="Mozilla/4.0 (compatible;MSIE5.5;Windows NT)"
        myheaders={"User-Agent":user_agent}
        r=requests.get(url,headers=myheaders)  
        if r.status_code==200:
           r.encoding="utf-8"
           return r.text
        return 
#html解析器  提取相关页面的url 当前词条的标题和摘要
"""
提取信息前 需要分析html结构位置

需要标题和摘要的位置

<dd class="lemmaWgt-lemmaTitle-title">

"""
#解析页面中所有的html 和需要的数据
class HtmlParser(object):
    #当前页面的URL 和HTML 下载器返回的网页内容 html_cont
    #传入当前页面url和下载页面返回的内容
    def parser(self,page_url,html_cont):
        #
        if page_url is None or html_cont is None:
            print "error"
            return
        soup =BeautifulSoup(html_cont,"html.parser",from_encoding="utf-8")
        new_urls=self._get_new_urls(page_url,soup)###########################
        new_data=self._get_new_data(page_url,soup)
        return new_urls,new_data
    #从页面下载内容内部提取所有的url 
    def _get_new_urls(self,page_url,soup):
        new_urls=set()#创建一个未爬取的url集合
        #提取所有a标记数据 并根据过滤条件过滤/view/1234.html  \d+ 匹配数字
        #links=soup.find_all("a",href=re.compile("/view/\d+\.htm"))
        links=soup.find_all("a",attrs={'target':'_blank'})#过滤target
        for link in links:
            #print "link:%s"%link
            new_url=link.get("href")
            #拼接完整的url
            new_full_url=urlparse.urljoin(page_url, new_url)
            #print "new_full_url:%s"%new_full_url
            new_urls.add(new_full_url)
        return new_urls
    #根据页面内容解析所有的数据并返回数据
    def _get_new_data(self,page_url,soup):
        #取出来的数据放到字典内
        datas=[]
        #匹配符合条件的行 再查找 h1  
        #分析html数据结构
        #print "page_url:%s"% page_url
        titles=soup.find_all("a",attrs={'target':'_blank'})#过滤target
        for title in titles: 
            data={}#字典内只存一对数据  
            if title is None:
                return  
            new_full_url=urlparse.urljoin("https://baike.baidu.com", title.get("href"))
            if title.string is not None:
                data["url"]=(new_full_url)
                data["title"]= ( title.get_text() )# title.string 
                datas.append(data)
        #xxxxxxxxxxxxxxxxxx只返回了循环最后一次的数据 其他数据都覆盖掉了
        return datas

#数据存储器
"""
store_data(data) 将解析的数据存储到内存中
output_html() 存储的数据输出到文件
"""
class DataOutput(object):
    def __init__(self):
        self.datas=[]#新建缓存列表
    def store_data(self,data):
        if data is None:
            return 
        self.datas=copy.deepcopy(data)#
        print "copy end"
        print self.datas
    def output_html(self):
        fout =codecs.open("baike.html","w",encoding="utf-8")
        fout.write("<html>")
        fout.write("""<head> <meta charset="UTF-8"><meta http-equiv="X-UA-Compatible" content="IE=Edge"> </head>""")
        fout.write("<body>")
        fout.write("<table>")
        for data in self.datas:
            fout.write("<tr>")
            fout.write("<td>%s</td>"%data["url"])
            fout.write("<td>%s</td>"%data["title"])
            fout.write("</tr>")
            self.datas.remove(data)#写完后移除数据
        fout.write("</table>")
        fout.write("</body>")    
        fout.write("</html>")    
        fout.close()
    def print_data(self):
        for data in self.datas:
            print data

class SpiderMan(object):
    def __init__(self):
        self.manager = UrlManger()
        self.downloader =HtmlDownloader()
        self.parser=HtmlParser()
        self.output=DataOutput()
    def crawl(self,root_url):
        #入口url  加入到未爬取的url集合
        self.manager.add_new_url(root_url)
        
        while(self.manager.has_new_url() and self.manager.old_url_size()<get_message_num):
            try:
                #从url中获取新的URL
                new_url=self.manager.get_new_url()
                #下载网页
                html_cont=self.downloader.download(new_url)
                #print html_cont
                #从下载的网页中抓取所以的url和数据
                new_urls,data=self.parser.parser(new_url, html_cont)
                #将网页中提取的url再加到未爬取的集合中循环爬取
                self.manager.add_new_urls(new_urls)
                #数据存储到文件
                #取一对数据
                self.output.store_data(data) #数据量少 可以都放到内存 数据大 应分批存储
                print "已抓取%s个链接 剩余%s个 " % (self.manager.old_url_size() ,self.manager.new_url_size())
            except Exception, e:
                print e
        print "start write html "
        #self.output.print_data()
        self.output.output_html()
        print "write end"           
if __name__ == '__main__':
    get_message_num=6
    root_url = "https://baike.baidu.com"
    spider_man=SpiderMan()
    spider_man.crawl(root_url)









