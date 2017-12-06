import requests
import time
from selenium import webdriver
from lxml import etree
import os
import re
import random
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'}
start_url = 'http://www.cnn.com/search/?q=Facebook'
driver = webdriver.PhantomJS(executable_path='E:\\GCSJ\\phantomjs\\bin\\phantomjs.exe')
def get_articles_per_page(page):
	url = ''
	if page == 1:
		url = start_url+'&size=10&type=article&sort=relevance'
	else:
		url = start_url+'&size=10&page='+str(page)+'&from='+str(10*(page-1))+'&type=article&sort=relevance'
	driver.get(url )
	time.sleep(3)
	html = driver.page_source
	selector  = etree.HTML(html)
	try:
		lists = selector.xpath('/html/body/div[5]/div[2]/div/div[2]/div[2]/div/div[3]')
	except Exception :
		return
	if len(lists) == 0:
		return
	for link in lists[0]:
		try:
			title = link.xpath('.//div[2]/h3/a/text()')
			content = link.xpath('.//div[2]/div/text()')
		except Exception as e:
			print(e)
			continue
		if title != None and content != None:
			store_article(title[0].strip(),''.join(content).strip())
def store_article(title,content):
	os.chdir(r'e:\GCSJ\FacebookNews\FacebookNewsFromCNN')
	title = re.sub(r"[\/\\\:\*\?\"\<\>\|]","",title)
	file = title +'.txt'
	if os.path.exists(file):
		return
	fp = open(file,'w',encoding='utf-8')
	fp.write(content)
	fp.close()
next_page = 47
if __name__ == '__main__':
	#每一页10篇新闻,爬取发现从200页开始已经很难找到标题含有关键字的新闻
	for page in range(1,200):
		time.sleep(random.randint(10,20))
		get_articles_per_page(page)
		next_page += 1
		print(next_page)