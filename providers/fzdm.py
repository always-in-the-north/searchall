from bs4 import BeautifulSoup

from manhua.worker import Worker
from manhua.database import Manhua, ManhuaSub, ManhuaSetting
from manhua.loggings import logger
from manhua.config import get_config

from downloaders.imgentity import ImgEntity
from providers.BaseProvider import BaseProvider

import queue
import re

import pysnooper


def get_max_manhua_id():
	setting = ManhuaSetting()
	basic_query = setting.select().where(ManhuaSetting.key == "manhua_id")
	count = basic_query.count()
	if count == 0:
		setting.key = "manhua_id"
		setting.value = "1"
		setting.save()
	else:
		setting = setting.get(ManhuaSetting.key == "manhua_id")
		setting.value = str(int(setting.value) + 1)
		setting.save()

	return setting.value

def get_max_manhua_sub_id():
	setting = ManhuaSetting()
	basic_query = setting.select().where(ManhuaSetting.key == "manhua_sub_id")
	count = basic_query.count()
	if count == 0:
		setting.key = "manhua_sub_id"
		setting.value = "1"
		setting.save()
	else:
		setting = setting.get(ManhuaSetting.key == "manhua_sub_id")
		setting.value = str(int(setting.value) + 1)
		setting.save()

	return setting.value



class Fzdm(BaseProvider):
	"""docstring for ClassName"""
	def __init__(self, arg = ""):
		super(Fzdm, self).__init__(arg)
		self._download_queue = queue.Queue(get_config("maxsizequeue", default = 10))
		self._worker = Worker()

	@property
	def download_queue(self):
		return self._download_queue
	
	def fetch_manhua(self, m: Manhua):
		basic_query = Manhua.select().where(
			Manhua.manhua_id == m.manhua_id)
		count = basic_query.count()
		if count == 0:
			# logger.debug('Creating new ip record: ' + p.__str__())
			m.save()
		else:
			# logger.debug('Update an existing ip record: ' + p.__str__())

			existing_manhua: Manhua = Manhua.get(
				Manhua.manhua_id == m.manhua_id)

			existing_manhua.set_value(m)

			existing_manhua.save()

			# logger.debug('Saved: ' + existing_proxy.__str__())

	def fetch_manhua_sub(self, m: ManhuaSub) -> bool:
		m.save()
		return True

		basic_query = ManhuaSub.select().where(
			ManhuaSub.manhua_id == m.manhua_id and 
			ManhuaSub.manhua_sub_id == m.manhua_sub_id and 
			ManhuaSub.yeshu == m.yeshu)

		count = basic_query.count()
		if count == 0:
			# logger.debug('Creating new ip record: ' + p.__str__())
			m.save()
		else:
			# logger.debug('Update an existing ip record: ' + p.__str__())

			existing_manhuasub: ManhuaSub = ManhuaSub.get(
				ManhuaSub.manhua_id == m.manhua_id and 
				ManhuaSub.manhua_sub_id == m.manhua_sub_id and 
				ManhuaSub.yeshu == m.yeshu)

			existing_manhuasub.set_value(m)
			existing_manhuasub.save()

			# img_length = self._worker.res_headers["Content-Length"]
			# img_last_modified = self._worker.res_headers["Last-Modified"]
			# 
			# if m.length == img_length and m.lastModified == img_last_modified:
			# 	pass					
			# else:
			# 	existing_manhuasub.set_value(m)
			# 	existing_manhuasub.save()

	# @pysnooper.snoop()
	def parse(self):
		rooturl = "https://manhua.fzdm.com/2/" 

		logger.debug('fetch manhua [{}] start...'.format(rooturl))

		self._worker = Worker()
		soup = self._worker.get_html(url = rooturl)		
		if soup is not None:
			li_items = soup.select("div#content li")
			logger.debug('manhua {} count {}'.format(soup.h2.string, len(li_items)))

			#li_items.reverse()
			if li_items is not None and len(li_items) > 0 :

				m = Manhua(biaoti = soup.h2.string , 
					zuixinhua = li_items[0].a["href"], 
					manhua_id = get_max_manhua_id(),
					wangluodizhi = rooturl)
				self.fetch_manhua(m)
				logger.debug('update manhua {} : {} '.format(m.biaoti, m))

				for li_item in li_items:
					url = rooturl + li_item.a["href"]
					soup_item = self._worker.get_html(url = url)
					navigation = soup_item.find("div", class_="navigation")

					self.get_image_url(soup_item, m, url)  
					
					nextpage = navigation.find("a", string = "下一页")

					while nextpage:
						soup_item = self._worker.get_html(url = url + "/" + nextpage["href"])
						navigation = soup_item.find("div", class_="navigation")						
						# print("打印" + navigation.find("a", class_ = "button-success").string)
						self.get_image_url(soup_item, m, url + "/" + nextpage["href"])						
						nextpage = navigation.find("a", string = "下一页")
		else:
			logger.debug('fetch result nothing.')

		logger.debug('fetch manhua end.')

	def get_image_url(self, soup, mhead, url):

		script = soup.find_all("script", string=re.compile(r'var Title="海贼王[第]*\d+.*";'))
		m = re.search(r'var mhurl="([\d\/\.\w]+)";', script[0].string)
		if m:
			for mhss in ['www-mipengine-org.mipcdn.com/i/p3.manhuapan.com', 'p1.manhuapan.com', 'p2.manhuapan.com', 'p4.manhuapan.com', 'p5.manhuapan.com']:
				try:
					mhurl = m.group(1)
					http = 'http://'

					navigation = soup.find("div", class_="navigation")		
					getyeshu = navigation.find("a", class_ = "button-success").string
					
					getyeshumatch = re.search(r".*?(\d+).*?", getyeshu)
					if getyeshumatch:
						getyeshu = getyeshumatch.group(1)

					ms = ManhuaSub(biaoti = soup.select("div#pjax-container")[0].h1.string,
								   yeshu = getyeshu,
								   wangluodizhi = http + mhss + '/' + mhurl,
								   wangyewangluodizhi = url,
								   manhua_id = mhead.manhua_id,
								   manhua_sub_id = get_max_manhua_sub_id()
					)


					logger.debug('update manhua sub {} : {} '.format(ms.biaoti, ms))
					
					if self.fetch_manhua_sub(ms):
						imgentity = ImgEntity()
						imgentity.wangluodizhi = http + mhss + '/' + mhurl					
						
						self._download_queue.put(imgentity, block = True, timeout = None)
						logger.debug('push imgentity to queue successfully. [{}] current size [{}]'.format(imgentity, self._download_queue.qsize()))

					break
				except Exception as e:
					raise e
					logger.warning('push imgentity to queue error.[{}]'.format(type(e)))
		else:
			print("None")



			# logger.debug('Saved: ' + existing_proxy.__str__())