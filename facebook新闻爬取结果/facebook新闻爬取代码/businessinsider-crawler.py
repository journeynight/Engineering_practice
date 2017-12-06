import requests
from bs4 import BeautifulSoup as bs4
import re
import time
import random
import os
import telnetlib
from lxml import etree

categories = [{'category':'Tech Insider','link':'sai'},{'category':'Enterprise','link':'enterprise'},
			{'category':'Science','link':'science'},{'category':'Media','link':'media'},
			{'category':'Transportation','link':'transportation'},{'category':'Finance','link':'clusterstock'},
			{'category':'Market','link':'moneygame'},{'category':'Retail','link':'retail'},
			{'category':'Wealthadvisor','link':'wealthadvisor'},{'category':'Yourmoney','link':'yourmoney'},
			{'category':'Politics','link':'politics'},{'category':'Military Defense','link':'defense'},
			{'category':'News','link':'news'},{'category':'Strategy','link':'warroom'},
			{'category':'Careers','link':'careers'},{'category':'Education','link':'education'},
			{'category':'Smallbusiness','link':'smallbusiness'},{'category':'Lists','link':'lists'},
			{'category':'Life','link':'thelife'},{'category':'Travel','link':'travel'},
			{'category':'Sports','link':'sportspage'}]

ips = [{'http':'http://185.106.121.192:1080'},{'http':'http://192.240.150.133:8080'},
	   {'http':'http://180.183.246.12:1080'},{'http':'http://179.182.213.66:1080'}]

header = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36 LBBROWSER',
		  'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
		  'Accept-Encoding':'gzip, deflate, sdch',
		  'Accept-Language':'zh-CN,zh;q=0.8',
	   	  'Cache-Control':'max-age=0',
		  'Connection':'keep-alive',
		  'Host':'www.businessinsider.com',
		  'Upgrade-Insecure-Requests':'1'}
def get_ips():
	os.chdir(r'e:\GCSJ')
	fp = open('ips.txt','r')
	ips = fp.readlines()
	fp.close()
	return ips
def get_Category_Urls(main_page_url):
	category_urls = []
	from selenium import webdriver
	driver = webdriver.PhantomJS(executable_path='E:\\GCSJ\\phantomjs\\bin\\phantomjs.exe')
	driver.get(main_page_url)
	time.sleep(10)
	html = driver.page_source
	selector = etree.HTML(html)
	divs = selector.xpath('/html/body/div[3]/div[3]/div/div[2]')
#get page nums 
def get_page_nums(start_url):
	html = requests.get(start_url).text
	soup = bs4(html,'lxml')
	pages = 1
	#ips = get_ips()
	while 1:
		pages += 1
		next_page_url = re.sub(r'\?.*','',start_url) + soup.find('li',{'class':'next'}).find('a')['href']
		time.sleep(random.randint(2,5))
		#proxies={'http':'http://'+ips[ip_index]}
		#ip_valid = 0
		# while ip_valid != 1:
		# 	ip_index = random.randint(0,len(ips)-1)
		# 	try:
		# 		telnetlib.Telnet(ips[ip_index].split(':')[0], ips[ip_index].split(':')[1], timeout=30)
		# 	except:
		# 		ip_valid = 0
		# 	else:
		# 		ip_valid = 1
		html = requests.get(next_page_url,headers = header ,timeout=60).text
		soup = bs4(html,'lxml')
		if soup.find('li',{'class':'next disabled'}) is not None:
			break
	return pages
#start from start_url
def get_article_urls(start_url):
	html = requests.get(start_url).text
	soup = bs4(html,'lxml')
	divs = soup.find('div',{'class':'river'}).findChildren()
	urls = []
	for div in divs:
		if div.name in ['h2','h3']:
			urls.append(div.find('a')['href'])
	return urls
def get_descendant_article_urls(url):
	urls = []
	html = requests.get(url,headers=header).text
	soup = bs4(html,'lxml')
	divs =  soup.findAll('div',{'class':'river'})
	for div in divs:
		urls.append(div.find('h3').find('a')['href'])
	return urls
def get_article_by_url(url):
	article = {}
	finalText = ''
	#ip_index = random.randint(0,len(ips)-1)
	#html = requests.get(url,headers=header,proxies=ips[ip_index]).text
	html = requests.get(url,headers=header).text
	soup = bs4(html,'lxml')
	try:
		target = soup.find('div',{'class':'clear-both'}).find('div',{'class':'KonaBody post-content'}) 
	except Exception as e:
		print(url,e)
		return None
	if target is None:
		return None
	for para in target.select('p'):
		rawText = re.sub(r'\n','',para.get_text().strip()) 
		rawText = re.sub(r'Â\xa0',' ',rawText)
		#a bug here,\' should be replaced with ', here just remove \'.
		rawText = re.sub(r'\'','',rawText)
		finalText += rawText
	article['content'] = finalText
	try:
		article['title'] = soup.find('div',{'class':'sl-layout-post'}).find('h1').get_text()
	except Exception as e:
		print(e,url)
	return article
def store_urls(path,start_url):
	pages = get_page_nums(start_url)
	urls = get_article_urls(start_url)
	for i in range(2,pages+1,1):
		url = start_url + '?page='+str(i)
		urls.extend(get_descendant_article_urls(url))
	os.chdir(path)
	fp = open('urls.txt','a')
	for url in urls:
		fp.write(url+'\n')
	fp.close()
def get_urls(path):
	os.chdir(path)
	fp = open('urls.txt','r')
	urls = fp.readlines()
	fp.close()
	return urls
def store_article(path,article):
	if article is None:
		return 
	file_name = article['title']+'.txt'
	#remove the invalid character in a filename under windows
	file_name = re.sub(r"[\/\\\:\*\?\"\<\>\|]","",file_name)
	os.chdir(path)
	if os.path.isfile(file_name):
		return
	try:
		#encodeing parameter is important
		fp = open(file_name,'w',encoding='utf-8')
		fp.write(article['content'])
	except Exception as e:
		print(e)
	fp.close()
def crawl_whole_site():
	for category in categories:
		os.chdir(r'e:\GCSJ\BusinessInsiderAllNews')
		file = category['category']
		if not os.path.isdir(file):
			os.mkdir(file)
		path = r'e:\GCSJ\BusinessInsiderAllNews'+'\\'+file
		os.chdir(path)
		start_url = 'http://www.businessinsider.com/'+ category['link']
		if not os.path.isfile('urls.txt'):
			store_urls(path,start_url)
			urls = get_urls(path)
			for url in urls:
				url = url.strip()
				time.sleep(random.randint(5,10))
				article = get_article_by_url(url)
				store_article(path,article)
			return
		else:
			continue
#get_Category_Urls('http://www.businessinsider.com')
if __name__ == '__main__':
	crawl_whole_site()