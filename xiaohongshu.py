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
	print('请输入商品名称：')
	keyword = '笔记本'
	rsp = requests.get(url.format(keyword, str(1)), headers=headers)
	print(rsp)                         
	if rsp.status_code == 200:
		text = json.loads(rsp.text)
		if (text.get('result')==0) and (text.get('success')) and (text.get('data').get('items')):
			return	parse(text), keyword
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
	for item in items:
		if {item.get('vendor_name'):item.get('seller_id')} not in sellers:
			sellers.append({item.get('vendor_name'):item.get('seller_id')})
	print(sellers)
	return sellers


def parse_store_products(sellers, keyword):
	print(sellers)
	store_url = 'https://www.xiaohongshu.com/api/store/vs/{store_id}/items/v2?page={page}'
	for seller in sellers:
		for seller_name, seller_id in seller.items():
			requests_store(store_url, seller_name, seller_id, keyword, i=1)


def requests_store(store_url, seller_name, seller_id, keyword, i=1):
	print('正在爬取店铺：', seller_name)
	for page in range(1, 100):
		print('正在爬取店铺：', seller_name, '第', page, '页')
		try:
			rsp = requests.get(store_url.format(store_id=seller_id, page=str(page)), headers=headers)
			if rsp.status_code == 200:
				if len(rsp.text) < 200:
					break
				else:
					parse_page(rsp.text, keyword)
			else:
				print('请求第二次', seller_name, store_url)
				time.sleep(random.randint(2, 6) + random.random() * 5)
				rsp = requests.get(store_url.format(store_id=seller_id, page=str(page)), headers=headers, timeout=15)
				if rsp.status_code == 200:
					if len(rsp.text) < 200:
						break
					else:
						parse_page(rsp.text, keyword)
				else:
					print('请求第三次', seller_name, store_url)
					time.sleep(random.randint(2, 6) + random.random() * 5)
					rsp = requests.get(store_url.format(store_id=seller_id, page=str(page)), headers=headers, timeout=15)
					if rsp.status_code == 200:
						if len(rsp.text) < 200:
							break
						else:
							parse_page(rsp.text, keyword)
					else:
						print('请求失败', seller_name)
		except:
			print('请求失败', seller_name, store_url)


def parse_page(text, keyword):
	items = json.loads(text)
	if items.get('success') and items.get('data'):
# if rsp.status_code == 200:# and items.get('success') and items.get('data'):
		for item in items.get('data'):
			data = {}
			data['id'] = item.get('id')
			data['category'] = keyword
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
			print(data)
			save_data(data)
		time.sleep(random.randint(2, 6) + random.random() * 5)
	else:
		pass
# else:
# 	i += 1
# 	time.sleep(random.randint(2, 6) + random.random() * 5)
# 	if i < 4:
# 		requests_store(store_url, seller_name, seller_id, i=i)
# 	else:
# 		pass

if __name__ == '__main__':
	sellers, keyword = start_requests()
	parse_store_products(sellers, keyword)





# # url = 'https://www.xiaohongshu.com/sapi/wx_mp_api/sns/v1/search/user?sid=session.1544597026443090585&keyword=%E5%B8%BD%E5%AD%90&page=2&rows=20 '
# # url = 'https://www.xiaohongshu.com/api/sns/v3/user/5bc5554b01c2a7000107d752/info?platform=android&deviceId=3a9501e1-2e45-3465-b806-9ec07cc886bd&device_fingerprint=201812121058460516c84f6654a93dfccdbb9409a6e1c901dab6ed505eab56&device_fingerprint1=201812121058460516c84f6654a93dfccdbb9409a6e1c901dab6ed505eab56&versionName=5.32.0&channel=YingYongBao&sid=session.1544597026443090585&lang=en&t=1544603071&sign=60cdbf0563be2b561eed4bbed9c05558'
# url = 'https://www.xiaohongshu.com/api/sns/v3/note/user/5bc5554b01c2a7000107d752?page=1&page_size=10&sub_tag_id=&platform=android&deviceId=3a9501e1-2e45-3465-b806-9ec07cc886bd&device_fingerprint=201812121058460516c84f6654a93dfccdbb9409a6e1c901dab6ed505eab56&device_fingerprint1=201812121058460516c84f6654a93dfccdbb9409a6e1c901dab6ed505eab56&versionName=5.32.0&channel=YingYongBao&sid=session.1544597026443090585&lang=en&t=1544603071&sign=2bc05f73e7ddaad07921783ca4b46b80'
# url = 'https://www.xiaohongshu.com/api/sns/v3/note/user/5bc5554b01c2a7000107d752?page=1&page_size=10&sub_tag_id=&platform=android&deviceId=3a9501e1-2e45-3465-b806-9ec07cc886bd&device_fingerprint=201812121058460516c84f6654a93dfccdbb9409a6e1c901dab6ed505eab56&device_fingerprint1=201812121058460516c84f6654a93dfccdbb9409a6e1c901dab6ed505eab56&versionName=5.32.0&channel=YingYongBao&sid=session.1544597026443090585&lang=en&t=1544604188&sign=23907e22f4ee3747063e5bef289b0b80'
# headers = {
# # 	# GET https://www.xiaohongshu.com/sapi/wx_mp_api/sns/v1/search/user?sid=session.1544597026443090585&keyword=%E5%B8%BD%E5%AD%90&page=2&rows=20 HTTP/1.1
# # 	'charset': 'utf-8',
# # 	'Accept-Encoding': 'gzip',
# # 	'referer': 'https://servicewechat.com/wxffc08ac7df482a27/147/page-frame.html',
# # 	'authorization': 'd6573b0f-3b2d-45a1-b8f7-43930173886c',
# # 	'auth': 'eyJoYXNoIjoibWQ0IiwiYWxnIjoiSFMyNTYiLCJ0eXAiOiJKV1QifQ.eyJzaWQiOiIxNmM0NzIzMmE5MTU0OGMxYzhjNGVjNWQ3YzJjM2MxOSIsImV4cGlyZSI6MTU0NDYwMjM4N30.mwYbk_-vxy8DUOjnOJjJaMmw-CWMvj-beR71jBsb4Ac',
# # 	'content-type': 'application/json',
# # 	'auth-sign': '4e4ed49ed6958ecc909d6e4aa5b4b9fb',
# # 	'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0.1; SM-C5010 Build/MMB29M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/71.0.3578.83 Mobile Safari/537.36 MicroMessenger/6.7.3.1360(0x2607036C) NetType/WIFI Language/en Process/toolsmp',
# # 	'Host': 'www.xiaohongshu.com',

# 	# 'Connection': 'Keep-Alive',
# 	# 'X-Tingyun-Id': 'LbxHzUNcfig;c=2;r=545747665;u=3f1ea2039402e0d7e1bc8059f51522d1e4d075dd70b92bf3eae8401f3954f50c3dcf37241527311d4a75ec1409388158::BE9A03AFFA4F5D68',
# 	# 'Authorization': 'session.1544597026443090585',
# 	# 'device_id': '3a9501e1-2e45-3465-b806-9ec07cc886bd',
# 	'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 6.0.1; SM-C5010 Build/MMB29M) Resolution/1080*1920 Version/5.32.0 Build/5320432 Device/(samsung;SM-C5010) NetType/WiFi',
# 	# 'shield': '1187ac31eb819aee1e23da244556429110df8cf7e6cb7e752ee9758414268be7',
# 	'shield': '91e58c3299754d8f0735df4602d9593de98bdcc9b15e15121396e044110e950a',
# 	'Host': 'www.xiaohongshu.com',
# 	'Connection': 'Keep-Alive',
# 	'Accept-Encoding': 'gzip',


# }

# rsp = requests.get(url, headers=headers)
# print(rsp)
# print(rsp.text)







# GET https://www.xiaohongshu.com/api/sns/v6/homefeed?oid=homefeed_recommend&cursor_score=1544665919.9900&geo=eyJsYXRpdHVkZSI6MzAuMzA4NDcyLCJsb25naXR1ZGUiOjEyMC4wOTQ2ODh9%0A&trace_id=47080195-09d4-36d0-8363-b718217e41f9&note_index=19&platform=android&deviceId=3a9501e1-2e45-3465-b806-9ec07cc886bd&device_fingerprint=201812121058460516c84f6654a93dfccdbb9409a6e1c901dab6ed505eab56&device_fingerprint1=201812121058460516c84f6654a93dfccdbb9409a6e1c901dab6ed505eab56&versionName=5.32.0&channel=YingYongBao&sid=session.1544597026443090585&lang=en&t=1544666203&sign=e9ed561e9d39440135a9ba4970dbc02e HTTP/1.1
# X-Tingyun-Id: LbxHzUNcfig;c=2;r=1711438978;u=917657fcd0f7c655aa7d76a6e58db561071dae7a63e067a77cdde096205528dcdbe1953ed249d08d208c912bd856258b::FE50E3887A421DC0
# Authorization: session.1544597026443090585
# device_id: 3a9501e1-2e45-3465-b806-9ec07cc886bd
# User-Agent: Dalvik/2.1.0 (Linux; U; Android 6.0.1; SM-C5010 Build/MMB29M) Resolution/1080*1920 Version/5.32.0 Build/5320432 Device/(samsung;SM-C5010) NetType/WiFi
# shield: d379b8fbd1789b264b54a4081ec4b669b6936ad181ba03e6e9ed93d80e62696c
# Host: www.xiaohongshu.com
# Connection: Keep-Alive
# Accept-Encoding: gzip


# GET https://www.xiaohongshu.com/api/sns/v6/homefeed?oid=homefeed_recommend&cursor_score=1544665919.9800&geo=eyJsYXRpdHVkZSI6MzAuMzA4NDcyLCJsb25naXR1ZGUiOjEyMC4wOTQ2ODh9%0A&trace_id=47080195-09d4-36d0-8363-b718217e41f9&note_index=29&platform=android&deviceId=3a9501e1-2e45-3465-b806-9ec07cc886bd&device_fingerprint=201812121058460516c84f6654a93dfccdbb9409a6e1c901dab6ed505eab56&device_fingerprint1=201812121058460516c84f6654a93dfccdbb9409a6e1c901dab6ed505eab56&versionName=5.32.0&channel=YingYongBao&sid=session.1544597026443090585&lang=en&t=1544666212&sign=90a46f50a5d94febb42ce51bd37242a0 HTTP/1.1
# X-Tingyun-Id: LbxHzUNcfig;c=2;r=471900144;u=917657fcd0f7c655aa7d76a6e58db561071dae7a63e067a77cdde096205528dcdbe1953ed249d08d208c912bd856258b::FE50E3887A421DC0
# Authorization: session.1544597026443090585
# device_id: 3a9501e1-2e45-3465-b806-9ec07cc886bd
# User-Agent: Dalvik/2.1.0 (Linux; U; Android 6.0.1; SM-C5010 Build/MMB29M) Resolution/1080*1920 Version/5.32.0 Build/5320432 Device/(samsung;SM-C5010) NetType/WiFi
# shield: 2b764d4b4f8de622bec77fd6041e9d184a5bfe68ffb4dc6e9a48f704ac74b782
# Host: www.xiaohongshu.com
# Connection: Keep-Alive
# Accept-Encoding: gzip


# GET https://www.xiaohongshu.com/api/sns/v6/homefeed?oid=homefeed_recommend&cursor_score=1544665919.9500&geo=eyJsYXRpdHVkZSI6MzAuMzA4NDcyLCJsb25naXR1ZGUiOjEyMC4wOTQ2ODh9%0A&trace_id=47080195-09d4-36d0-8363-b718217e41f9&note_index=59&platform=android&deviceId=3a9501e1-2e45-3465-b806-9ec07cc886bd&device_fingerprint=201812121058460516c84f6654a93dfccdbb9409a6e1c901dab6ed505eab56&device_fingerprint1=201812121058460516c84f6654a93dfccdbb9409a6e1c901dab6ed505eab56&versionName=5.32.0&channel=YingYongBao&sid=session.1544597026443090585&lang=en&t=1544666319&sign=e32cdf6ac2efe7a038585e40756125f3 HTTP/1.1
# X-Tingyun-Id: LbxHzUNcfig;c=2;r=719730073;u=917657fcd0f7c655aa7d76a6e58db561071dae7a63e067a77cdde096205528dcdbe1953ed249d08d208c912bd856258b::FE50E3887A421DC0
# Authorization: session.1544597026443090585
# device_id: 3a9501e1-2e45-3465-b806-9ec07cc886bd
# User-Agent: Dalvik/2.1.0 (Linux; U; Android 6.0.1; SM-C5010 Build/MMB29M) Resolution/1080*1920 Version/5.32.0 Build/5320432 Device/(samsung;SM-C5010) NetType/WiFi
# shield: 79c27194a1fca6c65d205d11e67b25b7f18c7ad760bd30b0af237f92e319531f
# Host: www.xiaohongshu.com
# Connection: Keep-Alive
# Accept-Encoding: gzip
