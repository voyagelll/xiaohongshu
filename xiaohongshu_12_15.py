# 商品接口： https://www.xiaohongshu.com/api/store/ps/products/v2?keyword=%E6%89%8B%E6%9C%BA&filters=&page=20&size=20&sort=&source=store_feed
import  requests
import json
import time 
import random
import re 
import ast 
from lxml import etree 
from fake_useragent import UserAgent
from multiprocessing.dummy import Pool as ThreadPool
import gevent 
from gevent import monkey 
gevent.monkey.patch_all()
from gevent.pool import Pool
from db import *


ua = UserAgent()
headers = {'User-Agent': ua.random}
redis = ReidsClient()
# proxies = redis.random()
# print(proxies)
url = 'https://www.xiaohongshu.com/api/store/ps/products/v2?keyword={}&filters=&page={}&size=1000&sort=&source=store_feed'


def get_products_list():
	raw_products_list = []
	products_list = []
	products_url = 'https://www.jd.com/allSort.aspx'
	rsp = requests.get(products_url, headers=headers)
	# print(rsp)
	doc = etree.HTML(rsp.text)
	itemss = doc.xpath('//dl[@class="clearfix"]')
	for items in itemss:
		item = items.xpath('dd/a/text()')
		for i in item:
			raw_products_list.append(i)
	for i in raw_products_list:
		if i not in products_list:
			products_list.append(i)
	print(len(products_list))
	return products_list

# get_products_list()


def start_requests(keyword, i=1):
	try:
		rsp = requests.get(url.format(keyword, str(1)), headers=headers, proxies=redis.random(), timeout=15)
	except:
		start_requests(keyword)
	else:
		if i == 1:
			print('第%s次请求 "%s" 类别' % (i, keyword))
		print('状态码', rsp)
		if rsp.status_code == 200 :
			text = json.loads(rsp.text)
			if len(rsp.text) < 250:
				print('无相关店铺...')
				with open('store_not_found.txt', 'a', encoding='utf-8') as f:
					f.write(keyword + '\n')
			else:
				sellers = []
				if text.get('data').get('recommend_items') or text.get('data').get('items'):
					recommend_items = text.get('data').get('recommend_items')
					if len(text.get('data').get('recommend_items')):
						for recommend_item in recommend_items:
							if {recommend_item.get('vendor_name'):recommend_item.get('seller_id')} not in sellers:
								sellers.append({recommend_item.get('vendor_name'):recommend_item.get('seller_id')})

					if len(text.get('data').get('items')):
						items = text.get('data').get('items')	
						sellers = []
						if items is not None:
							for item in items:
								if {item.get('vendor_name'):item.get('seller_id')} not in sellers:
									sellers.append({item.get('vendor_name'):item.get('seller_id')})
					if sellers is not None:
						stores = {'category': keyword, 'stores': sellers}
						save_stores_data(stores)

		else:
			i += 1
			if i < 4:
				print('第%s次请求 %s 类别' % (i, keyword))
				start_requests(keyword, i=i)
			else:
				with open('store_not_found.txt', 'a', encoding='utf-8') as f:
					f.write('请求失败' + keyword + '\n')


# ==============================================================================================================================


def parse_store_products(items):
	print(items)
	store_url = 'https://www.xiaohongshu.com/api/store/vs/{store_id}/items/v2?page={page}'
	for seller in items: #sellers[:1]:
		category = seller.get('category')
		stores = seller.get('stores')
		for store in stores:
			datas = []
			(seller_name, seller_id), = store.items()
			datas = requests_store(datas, category, store_url, seller_name, seller_id, i=1)
			save_products_data({'category': category, 'store':seller_name, 'store_id': seller_id, 'products':datas})


def requests_store(datas, category, store_url, seller_name, seller_id, i=1):
	print('正在爬取店铺：', seller_name)
	for page in range(1, 100):
		try:
			rsp = requests.get(store_url.format(store_id=seller_id, page=str(page)),  headers=headers,  timeout=15)
		except:
			requests_store(datas, category, store_url, seller_name, seller_id, i=1)
		else:
			if rsp.status_code == 200:
				if len(rsp.text) < 200:
					pass
				else:
					items = json.loads(rsp.text)
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
							time.sleep(3)

							datas.append(data)
			else:
				if i < 4:
					print('第 %s 次请求 %s' % (i, store_url))
					parse_page(page, category, store_url, seller_name, seller_id, i=i)
					i += 1
				else:
					pass
		
	return datas


if __name__ == '__main__':
	# 1171
	# for keyword in get_products_list()[1:10]:
	# 	start_requests(keyword)

	# pool = ThreadPool(20)
	# pool.map(start_requests, get_products_list()[:20])
	# pool.close()
	# pool.join()

	# products_list = get_products_list()[:]
	# pool = Pool(200)
	# pool.map(start_requests, [keyword for keyword in products_list])
	# pool.kill()
	# pool.join()

	# parse_store_products(sellers)


	items = read_stores_data()
	parse_store_products(items)








# def requests_store(category, store_url, seller_name, seller_id, i=1):
# 	print('正在爬取店铺：', seller_name)
# 	for page in range(1, 4):
# 		datas = []
# 		print('正在爬取店铺：', seller_name, '第', page, '页')
# 	# try:
# 		rsp = requests.get(store_url.format(store_id=seller_id, page=str(page)), headers=headers)
# 		if rsp.status_code == 200:
# 			if len(rsp.text) < 200:
# 				break
# 			else:
# 				data = parse_page(rsp.text)
# 		else:
# 			print('请求第二次', seller_name, store_url)
# 			time.sleep(random.randint(2, 6) + random.random() * 5)
# 			rsp = requests.get(store_url.format(store_id=seller_id, page=str(page)), headers=headers, proxies=redis.random())
# 			if rsp.status_code == 200:
# 				if len(rsp.text) < 200:
# 					break
# 				else:
# 					data = parse_page(rsp.text)
# 			else:
# 				print('请求第三次', seller_name, store_url)
# 				time.sleep(random.randint(2, 6) + random.random() * 5)
# 				rsp = requests.get(store_url.format(store_id=seller_id, page=str(page)), headers=headers, proxies=redis.random())
# 				if rsp.status_code == 200:
# 					if len(rsp.text) < 200:
# 						break
# 					else:
# 						data = parse_page(rsp.text)
# 				else:
# 					print('请求失败', seller_name)
# 		datas.append(data)
# 	save_stores_data({'category': category, 'stores':datas})
# 	# except:
# 	# 	print('请求失败', seller_name, store_url)
# {'category': '电气开关', 'stores': [{'柠檬日记旗舰店': '5baef71e2ba68e28ec393020'}, {'EIGHT ORANGES品牌店': '5ad5b9c81ed7f327420de2ce'}]}


# def parse_page(text):
# 	items = json.loads(text)
# 	if items.get('success') and items.get('data'):
# 		for item in items.get('data'):
# 			data = {}
# 			data['id'] = item.get('id')
# 			# data['category'] = keyword
# 			data['seller_id'] = item.get('seller_id')
# 			data['title'] = item.get('title') 
# 			data['desc'] = item.get('desc') 
# 			data['price'] = item.get('price')
# 			data['discount_price'] = item.get('discount_price')
# 			data['stock_status'] = item.get('stock_status') 
# 			try:
# 				data['link'] = item.get('link')[item['link'].index('www'):]
# 			except:
# 				pass
# 			data['promotion_text'] = item.get('promotion_text')
# 			data['vendor_icon'] = item.get('vendor_icon')
# 			data['vendor_name'] = item.get('vendor_name') 
# 			data['vnedor_link'] = item.get('vnedor_link') 
# 			data['buyable'] = item.get('buyable')
# 			data['new_arriving'] = item.get('new_arriving') 
# 			data['feature'] = item.get('feature')
# 			data['time'] = item.get('time')
# 			data['tax_included'] = item.get('tax_included')
# 			try:
# 				data['origin_price'] = item.get('item_price').get(1).get('price')
# 			except:
# 				pass
# 			try:
# 				data['sale_price'] = item.get('item_price').get(0).get('price')
# 			except:
# 				pass
# 			data['tags'] = item.get('tags')
# 			data['height'] = item.get('height')
# 			data['width'] = item.get('width') 
# 			data['stock_shortage'] = item.get('stock_shortage')
# 			yield data
# 			# print(data)
# 			# save_data(data)
# 		time.sleep(random.randint(3, 6) + random.random() * 10)
# 	else:
# 		pass


# if __name__ == '__main__':
# 	# 1171
# 	# for keyword in get_products_list()[1:10]:
# 	# 	start_requests(keyword)

# 	# pool = ThreadPool(20)
# 	# pool.map(start_requests, get_products_list()[:20])
# 	# pool.close()
# 	# pool.join()

# 	# products_list = get_products_list()[:]
# 	# pool = Pool(200)
# 	# pool.map(start_requests, [keyword for keyword in products_list])
# 	# pool.kill()
# 	# pool.join()

# 	# parse_store_products(sellers)


# 	items = read_stores_data()
# 	parse_store_products(items)

