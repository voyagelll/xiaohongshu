import os 
import time
import random
import pymongo
from appium import webdriver 
from appium.webdriver.common.touch_action import TouchAction 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.common.exceptions import NoSuchElementException 
from selenium.webdriver.common.by import By 
from selenium.webdriver.support import expected_conditions as EC 


PLATFORM = 'Android'
DEVICE_NAME = 'SM_C5010'
APP_PACKAGE = 'com.xingin.xhs'
APP_ACTIVITY = '.activity.SplashActivity'

# {
#   "platformName": "Android",
#   "deviceName": "SM_C5010",
#   "appPackage": "com.xingin.xhs",
#   "appActivity": ".activity.SplashActivity",
#   "unicodeKeyboard": "True",
#   "resetKeyboard": "True"
# }

DRIVER_SERVER = 'http://127.0.0.1:4723/wd/hub'
TIMEOUT = 299
MONGO_URL = 'localhost'
MONGO_DB = 'bihu_project'
MONGO_COLLECTION = 'xiaohongshu_template'

FLICK_START_X = 300 
FLICK_START_Y = 100 
FLICK_DISTANCE = 1000


class Moments(object):
	def __init__(self):
		self.desired_caps = {
			'platform': PLATFORM,
			'deviceName': DEVICE_NAME,
			'appPackage': APP_PACKAGE,
			'appActivity': APP_ACTIVITY,
			'unicodeKeyboard': 'True',
            'resetKeyboard': 'True'
		}
		self.driver = webdriver.Remote(DRIVER_SERVER, self.desired_caps)
		self.wait = WebDriverWait(self.driver, TIMEOUT)
		self.client = pymongo.MongoClient(MONGO_URL)
		self.db = self.client[MONGO_DB]
		self.collection = self.db[MONGO_COLLECTION]


	def login(self):
		el1 = self.wait.until(EC.presence_of_element_located((By.ID, "android:id/button1")))
		time.sleep(3)
		el1.click()
		el2 = self.wait.until(EC.presence_of_element_located((By.ID, "com.android.packageinstaller:id/permission_allow_button")))
		time.sleep(3)
		el2.click()
		time.sleep(3)
		el2.click()
		el3 = self.driver.find_element_by_xpath("/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.RelativeLayout/android.widget.LinearLayout[2]/android.widget.RelativeLayout[1]/android.widget.RelativeLayout/android.widget.LinearLayout/android.widget.TextView")
		time.sleep(30)
		el3.click()
		el4 = self.wait.until(EC.presence_of_element_located((By.ID, "com.xingin.xhs:id/searchView")))
		el4.click()
		time.sleep(3)
		el5 = self.wait.until(EC.presence_of_element_located((By.ID, "com.xingin.xhs:id/mEtSearchBarHitRight")))
		time.sleep(3)
		el5.click()
		el5.send_keys("学习")
		time.sleep(3)
		el6 = self.wait.until(EC.presence_of_element_located((By.ID, "com.xingin.xhs:id/mSearchToolBarCancel")))
		el6.click()

	def crawl(self):
		while True:
			self.driver.swipe(FLICK_START_X, FLICK_START_Y + FLICK_DISTANCE, FLICK_START_X, FLICK_START_Y)
			time.sleep(random.random() * 5)
			# items = self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@resource-id="com.tencent.mm:id/e2p"]//android.widget.FrameLayout')))
			# # print(str(items))
			# print(items)
			# try:
			# # for item in items:
			# 	nickname = items.find_element_by_id('com.tencent.mm:id/azl').get_attribute('text')
			# 	content = items.find_element_by_id('com.tencent.mm:id/jv').get_attribute('text')
			# 	date = items.find_element_by_id('com.tencent.mm:id/e25').get_attribute('text')
			# 	print(nickname, content, date)
			# except Exception as e:
			# 	print(e)

	def main(self):
		self.login()
		self.crawl()


if __name__ == '__main__':
	weixin = Moments()
	weixin.main()

# 1680