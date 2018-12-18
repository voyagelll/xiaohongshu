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
				if text.get('data').get('items'):
					if len(text.get('data').get('items')):
						items = text.get('data').get('items')	
						sellers = []
						if items is not None:
							for item in items:
								if {item.get('vendor_name'):item.get('seller_id')} not in sellers:
									sellers.append({item.get('vendor_name'):item.get('seller_id')})
					if sellers is not None:
						for seller in sellers:
							(seller_name, seller_id), = seller.items()
							save_stores_data({'category': keyword, 'seller_name':seller_name, 'seller_id': seller_id})

		else:
			i += 1
			if i < 4:
				print('第%s次请求 %s 类别' % (i, keyword))
				start_requests(keyword, i=i)
			else:
				with open('store_not_found.txt', 'a', encoding='utf-8') as f:
					f.write('请求失败' + keyword + '\n')


# ==============================================================================================================================

# def requests_products(store_url, seller_name, seller_id, page):
# 	try:
# 		rsp = requests.get(store_url.format(store_id=seller_id, page=str(page)), headers=headers, proxies=redis.random(), timeout=15)
# 		# print(rsp.status_code, len(rsp.text))
# 		print('正在爬取"%s"第 %s 页, 状态码：%s, 返回数据大小：%s' % (seller_name, page, rsp.status_code, len(rsp.text)))
# 		if len(rsp.text) > 100:
# 			text = rsp.text
# 			if rsp.status_code == 200:
# 				return text
# 			else:
# 				requests_products(store_url, seller_name, seller_id, page)
# 		else:
# 			return 0
# 	except:
# 		requests_products(store_url, seller_name, seller_id, page)



def parse_store_products(seller):
	store_url = 'https://www.xiaohongshu.com/api/store/vs/{store_id}/items/v2?page={page}'
	seller_name = seller.get('seller_name')
	seller_id = seller.get('seller_id')
	category = seller.get('category')

	print('正在爬取店铺：', seller_name)
	datas = []
	for page in range(1, 100):
		i = 1
		try:
			rsp = requests.get(store_url.format(store_id=seller_id, page=str(page)), headers=headers, proxies=redis.random(), timeout=15)
			rsp.status_code == 200
		except:
			try:
				rsp = requests.get(store_url.format(store_id=seller_id, page=str(page)), headers=headers, proxies=redis.random(), timeout=15)
				rsp.status_code == 200
			except:
				try:
					rsp = requests.get(store_url.format(store_id=seller_id, page=str(page)), headers=headers, proxies=redis.random(), timeout=15)
					rsp.status_code == 200
				except:
					try:
						rsp = requests.get(store_url.format(store_id=seller_id, page=str(page)), headers=headers, proxies=redis.random(), timeout=15)
						rsp.status_code == 200
					except:
						try:
							rsp = requests.get(store_url.format(store_id=seller_id, page=str(page)), headers=headers, proxies=redis.random(), timeout=15)
							rsp.status_code == 200
						except:
							break

		text = rsp.text
		# text = requests_products(store_url, seller_name, seller_id, page)
		print('正在爬取"%s"第 %s 页, 状态码：%s, 返回数据大小：%s' % (seller_name, page, rsp.status_code, len(rsp.text)))
		# print(rsp.status_code, len(rsp.text))
		if len(text) <= 100:
			break
		elif rsp.status_code == 200 and len(text) > 200:
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
					# time.sleep(3)
					datas.append(data)

	# except:
	# 	break
	print(len(datas))
	save_products_data({'category':category, 'seller':seller_name, 'seller_id':seller_id, 'products':datas})
						# print(datas)

		# time.sleep(random.random()*5)


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



	items = read_stores_data()
	# for item in items:
	# parse_store_products(items[0])

	# items = read_stores_data()
	# pool = ThreadPool(10)
	# pool.map(parse_store_products, items)
	# pool.close()
	# pool.join()

	# products_list = get_products_list()[:]
	pool = Pool(100)
	pool.map(parse_store_products, [item for item in items])
	pool.kill()
	pool.join()



