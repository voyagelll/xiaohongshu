import pymongo
import redis 
import random 

# redis配置
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_PASSWORD = None 
REDIS_KEY = 'proxies'

# mongo配置
client = pymongo.MongoClient(host='localhost')
dbm = client.bihu_project

class ReidsClient(object):
	def __init__(self):
		self.db = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)
	def random(self):
		result = self.db.zrangebyscore(REDIS_KEY, 10, 10)
		if len(result):
			proxy = random.choice(result)
			if isinstance(proxy, bytes):
				proxy = proxy.decode('utf-8')
				proxies = {
					'http': 'http://' + proxy,
					'https': 'https://' + proxy,
				}
				print('正在使用代理：', proxies['http'])
				return proxies

# redis = ReidsClient()
# redis.random()

def save_stores_data(data):
# try:
	if dbm.xiaohongshu_stores_id.insert(data, check_keys=False):
		print('Save successfully...')
# except:
# 	print('Save failed...')


def save_products_data(data):
	try:
		if dbm.xiaohongshu_products.insert(data, check_keys=False):
			print('Save successfully...')
	except:
		print('Save failed...')


def read_stores_data():
	data = []
	for item in dbm.xiaohongshu_stores_id.find()[:]:
		# print(type(item))
		# print(item)
		data.append(item)
	return data[:100]


# items = read_stores_data()
# print(items)
# ids = []
# for item in items:
# 	if item.get('seller_id') not in ids:
# 		ids.append(item.get('seller_id'))

# 		save_stores_data(item)


