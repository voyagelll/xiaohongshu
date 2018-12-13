import pymongo

client = pymongo.MongoClient(host='localhost')
dbm = client.bihu_project

def save_data(data):
	try:
		if dbm.xiaohongshu_products.insert(data):
			print('Save successfully...', data)
	except:
		print('Save failed...')



