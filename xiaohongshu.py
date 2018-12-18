# 商品接口： https://www.xiaohongshu.com/api/store/ps/products/v2?keyword=%E6%89%8B%E6%9C%BA&filters=&page=20&size=20&sort=&source=store_feed
import  requests
import json
import time 
import random
import re 
from lxml import etree 
from fake_useragent import UserAgent
from db import *

ua = UserAgent()
headers = {'User-Agent': ua.random}
redis = ReidsClient()
proxies = redis.random()
# print(proxies)
url = 'https://www.xiaohongshu.com/api/store/ps/products/v2?keyword={}&filters=&page={}&size=1000&sort=&source=store_feed'


def get_products_list():
	products_list = []
	products_url = 'https://www.jd.com/allSort.aspx'
	rsp = requests.get(products_url, headers=headers)
	print(rsp)
	doc = etree.HTML(rsp.text)
	itemss = doc.xpath('//dl[@class="clearfix"]')
	for items in itemss:
		item = items.xpath('dd/a/text()')
		for i in item:
			products_list.append(i)
	# print(products_list)
	# print(len(products_list))
	return products_list


def start_requests(i=1):
	# print('请输入商品名称：')
	# keyword = '笔记本'
	products = get_products_list()
	# print(products)
	print(products[3:10])
	for keyword in products[3:10]:
		print(keyword)
		rsp = requests.get(url.format(keyword, str(1)), headers=headers)
		print(rsp)
		if rsp.status_code == 200 and rsp.text is not None:
			text = json.loads(rsp.text)
			if len(text.get('data').get('items')):
				return	parse(text)
		else:
			time.sleep(random.randint(2, 6) + random.random() * 5)
			i += 1
			if i < 4:
				print('第%s次请求%s' % (i, url))
				start_requests(i=i)
			else:
				pass


def parse(text):
	items = text.get('data').get('items')
	sellers = []
	if items is not None:
		for item in items:
			if {item.get('vendor_name'):item.get('seller_id')} not in sellers:
				sellers.append({item.get('vendor_name'):item.get('seller_id')})
		if sellers is not None:
			print(sellers)
			return sellers


def parse_store_products(sellers):
	store_url = 'https://www.xiaohongshu.com/api/store/vs/{store_id}/items/v2?page={page}'
	for seller in sellers[:1]:
		for seller_name, seller_id in seller.items():
			requests_store(store_url, seller_name, seller_id, i=1)


def requests_store(store_url, seller_name, seller_id, i=1):
	print('正在爬取店铺：', seller_name)
	for page in range(1, 2):
		print('正在爬取店铺：', seller_name, '第', page, '页')
	# try:
		rsp = requests.get(store_url.format(store_id=seller_id, page=str(page)), headers=headers, proxies=proxies)
		if rsp.status_code == 200:
			if len(rsp.text) < 200:
				break
			else:
				parse_page(rsp.text)
		else:
			print('请求第二次', seller_name, store_url)
			time.sleep(random.randint(2, 6) + random.random() * 5)
			rsp = requests.get(store_url.format(store_id=seller_id, page=str(page)), headers=headers, proxies=proxies)
			if rsp.status_code == 200:
				if len(rsp.text) < 200:
					break
				else:
					parse_page(rsp.text)
			else:
				print('请求第三次', seller_name, store_url)
				time.sleep(random.randint(2, 6) + random.random() * 5)
				rsp = requests.get(store_url.format(store_id=seller_id, page=str(page)), headers=headers, proxies=proxies)
				if rsp.status_code == 200:
					if len(rsp.text) < 200:
						break
					else:
						parse_page(rsp.text)
				else:
					print('请求失败', seller_name)
	# except:
	# 	print('请求失败', seller_name, store_url)


def parse_page(text):
	items = json.loads(text)
	if items.get('success') and items.get('data'):
		for item in items.get('data'):
			data = {}
			data['id'] = item.get('id')
			# data['category'] = keyword
			data['seller_id'] = item.get('seller_id')
			data['title'] = item.get('title') 
			data['desc'] = item.get('desc') 
			data['price'] = item.get('price')
			data['discount_price'] = item.get('discount_price')
			data['stock_status'] = item.get('stock_status') 
			try:
				data['link'] = item.get('link')[item['link'].index('www'):]
			except:
				pass
			data['promotion_text'] = item.get('promotion_text')
			data['vendor_icon'] = item.get('vendor_icon')
			data['vendor_name'] = item.get('vendor_name') 
			data['vnedor_link'] = item.get('vnedor_link') 
			data['buyable'] = item.get('buyable')
			data['new_arriving'] = item.get('new_arriving') 
			data['feature'] = item.get('feature')
			data['time'] = item.get('time')
			data['tax_included'] = item.get('tax_included')
			try:
				data['origin_price'] = item.get('item_price').get(1).get('price')
			except:
				pass
			try:
				data['sale_price'] = item.get('item_price').get(0).get('price')
			except:
				pass
			data['tags'] = item.get('tags')
			data['height'] = item.get('height')
			data['width'] = item.get('width') 
			data['stock_shortage'] = item.get('stock_shortage')
			# print(data)
			# save_data(data)
		time.sleep(random.randint(3, 6) + random.random() * 10)
	else:
		pass


if __name__ == '__main__':
	sellers = start_requests()
	parse_store_products(sellers)





