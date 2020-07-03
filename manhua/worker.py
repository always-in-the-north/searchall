import requests

from typing import Union
import os 

from peewee import SqliteDatabase

from manhua.config import get_config
from manhua.loggings import logger
from manhua.customexception import SqliteDbFilenotFoundError

from downloaders.imgentity import ImgEntity
from downloaders.downloader import DownLoader

import pysnooper
from bs4 import BeautifulSoup

class ProxiesWorker(object):

	_proxies_db = None
	def __init__(self, https = False, anonymous = False):
		super(object, self).__init__()

		self.create_connection()

		self._https = https
		self._anonymous = anonymous
	
	def create_connection(self) -> SqliteDatabase:
		"""
		create a database connection
		:rtype: SqliteDatabase
		"""
		if self._proxies_db:
			return self._proxies_db
		else: 
			# logger.debug('create new db connection')
			if(not os.path.exists(get_config('db_path', './scylla.db'))):
				raise SqliteDbFilenotFoundError("Sqlit db file not exists")

			self._proxies_db = SqliteDatabase(get_config('db_path', './scylla.db'))
			return self._proxies_db

	
	def _get_valid_proxies_query(self):
		query = "SELECT ip, port, is_https FROM proxy_ips where latency > 0 and latency < 9999 and is_valid = '1'" 
		query = query + " and is_https = '" + ("1" if self._https else "0") + "'"
		query = query + " and is_anonymous = '" + ("1" if self._anonymous else "0") + "'"

		cursor = self._proxies_db.execute_sql(query)
		return [(i[0], i[1], i[2]) for i in cursor]
		
	#@pysnooper.snoop()
	def get_proxies(self) -> tuple:
		proxies_list = self._get_valid_proxies_query()		
		import random
		r = random.choice(proxies_list)
		proxy : tuple = r
		proxy_str = "{}://{}:{}".format("https" if proxy[2] == "1" else "http", proxy[0], proxy[1]) 
		proxies = {"https": proxy_str, "http": proxy_str}

		# logger.debug('change proxies successfully,{} ...'.format(proxies))
		return proxies

class Worker(object):
	"""docstring for ClassName"""

	_get_count = 0
	_proxies_error_count = 0
	_error_count = 0

	def __init__(self, hFlag = True, pFlag = False):
		super(object, self).__init__()
		self._session = requests.session()

		self.headers = {
						"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36",
						"upgrade-insecure-requests":"1",
					}

		self.proxies = {}
		self.proxiesWorker = ProxiesWorker()
		self.change_proxy()

		self.headersFlag = hFlag
		self.proxiesFlag = pFlag

		self._res_headers = {} 
		self._res_Object = None 

	def change_proxy(self):
		self.proxies = self.proxiesWorker.get_proxies()
		logger.info('change proxies to {} ...'.format(self.proxies))

	@property
	def res_headers(self):
		return self._res_headers

	@property
	def res_Object(self):
		return self._res_Object

	def get_img(self, imgentity : ImgEntity) -> bool:
		try:
			d = DownLoader()
			imgentity = d.get(imgentity)
		except Exception as e:
			raise
		else:
			pass
		finally:
			pass

	def get_html(self, url) -> Union[BeautifulSoup, None]:
		r = None

		errpoint = 0 if self._proxies_error_count == 0 else (self._proxies_error_count / (self._get_count + self._proxies_error_count))

		if self.proxiesFlag == False and errpoint > 0.5:
			self.proxiesFlag = True
			self.change_proxy()

		if self.proxiesFlag and errpoint > 0.5:
			self._get_count = 0			
			self.change_proxy()

		try:

			self.headers = self.headers if self.headersFlag else None
			self.proxies = self.proxies if self.proxiesFlag else None
			logger.info('parse html {} start, proxies {} ...'.format(url, self.proxies))

			with self._session.get(url, headers = self.headers, 
										proxies = self.proxies, 
										timeout= 15 ) as res:
				if res.ok:
					self._res_Object = res
					self._res_headers = res.headers
					r = BeautifulSoup(res.content, "lxml")
					
					self._error_count = 0 
					self._proxies_error_count = 0
					self._get_count += 1

		except requests.RequestException as e:
			# todo
			if isinstance(e, requests.exceptions.ConnectTimeout) or \
				isinstance(e, requests.exceptions.ReadTimeout) or \
				isinstance(e, requests.exceptions.ProxyError) or \
				isinstance(e, requests.exceptions.ConnectionError):				
				# self.change_proxy()
				self._proxies_error_count += 1 
				logger.info('proxies error, info {}, {} times...'.format(type(e), self._proxies_error_count))
				return self.get_html(url)
			else:				
				self._error_count += 1				
				if self._error_count <= get_config('error_count', 3):				
					self.change_proxy()
					logger.info('wait for re-parsing html  , info {}, {} times...'.format(type(e), self._error_count))
					return self.get_html(url)

		except (KeyboardInterrupt, SystemExit, InterruptedError):
			self.stop()
			return None
		except Exception as e:
			raise
		else:
			pass
		finally:
			pass

		return r

	def stop(self):
		"""Clean the session
		"""

		self._session.close()



