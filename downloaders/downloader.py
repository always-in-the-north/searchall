import sys
import requests
import io
import os
import hashlib
import time

from manhua.loggings import logger
from .imgentity import ImgEntity
from manhua.utils import get_format_time
from manhua.config import get_config
from manhua.database import ManhuaSub

import pysnooper

class DownLoader(object):
	__retrycount = 1
	__readtime = 5
	__connecttime = 5

	"""docstring for ClassName"""
	def __init__(self, folderpath = "E:\\python\\manhua\\downloaders\\download\\", sleeptime = 3):
		super(DownLoader, self).__init__()
		self.folderpath = folderpath
		self.sleeptime = sleeptime


	def get_img_path(self, md5_str, entity):
		# 获取图片路径
		from manhua.utils import get_format_time
		return self.folderpath + get_format_time("1") + "_" + md5_str + "." + entity.kuozhanming

	def get_img_kuozhanming(self, res):
		# 获取图片扩展名
		if(res.headers["Content-Type"] == "image/jpeg"):
			return "jpg"
		elif(res.headers["Content-Type"] == "image/gif"):
			return "gif"
	# @pysnooper.snoop()
	def get(self, entity):
		headers = {
		    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36",
		    "cookie": "picHost=www-mipengine-org.mipcdn.com/i/p3.manhuapan.com; \
		               _ga=GA1.1.726297105.1589200721; \
		               _ga_1FZE0C2L80=GS1.1.1589465193.9.1.1589465605.0",
		    "upgrade-insecure-requests":"1",

		}
		if isinstance(entity, ImgEntity):
			# 图片类型
			logger.debug('download {} start ...'.format(entity.wangluodizhi))
			res = None
			try:
				with requests.get(entity.wangluodizhi, headers = headers,\
					                                   timeout = (self.__connecttime, self.__readtime)) as res:
					entity.kuozhanming = self.get_img_kuozhanming(res)
					imgpath = self.get_img_path(hashlib.md5(res.content).hexdigest(), entity)
					entity.bendidizhi = imgpath

					with open(imgpath, "wb") as f:
						f.write(res.content)

					m = ManhuaSub.update({
						"bendidizhi":imgpath,
						"length":res.headers["Content-Length"],
						"lastModified":res.headers["Last-Modified"]
						}).where(ManhuaSub.wangluodizhi == entity.wangluodizhi)
					m.execute()
					m = m.get(ManhuaSub.wangluodizhi == entity.wangluodizhi)

					logger.debug('download {} end, img info [{}].'.format(m.biaoti, entity))
					time.sleep(self.sleeptime)

					self.__retrycount = 1
					self.__readtime = 5
					self.__connecttime = 5

					return entity

			except requests.exceptions.ConnectionError as e:
				# todo
				logger.debug('download {} read connect error, wait for re-download {} times'.format(entity.wangluodizhi, self.__retrycount))
				
				if self.__retrycount < get_config("retrytimes"): 
					self.__retrycount += 1
					time.sleep(get_config("resleeptime"))
					self.get(entity)

			except requests.exceptions.ReadTimeout as e:
				# todo
				logger.debug('download {} read timeout, wait for re-download {} times'.format(entity.wangluodizhi, self.__retrycount))
				
				if self.__retrycount < get_config("retrytimes"): 
					self.__retrycount += 1
					self.__readtime += 3
					time.sleep(get_config("resleeptime"))
					self.get(entity)
					

			except requests.exceptions.ConnectTimeout as e:
				# todo
				logger.debug('download {} connect timeout, wait for re-download {} time'.format(entity.wangluodizhi, self.__retrycount))
				if self.__retrycount < get_config("retrytimes"): 
					self.__retrycount += 1
					self.__connecttime += 3
					time.sleep(get_config("resleeptime"))
					self.get(entity)
					

			except Exception as e:
				logger.debug('download {} error, error info {}, stop download'.format(entity.wangluodizhi,  e ))
			finally:
				res = None

def test():
	d = DownLoader()
	img = ImgEntity("")
	img.wangluodizhi = "http://www-mipengine-org.mipcdn.com/i/p3.manhuapan.com/2020/06/0514301923397.jpg"
	for n in range(2):
		d.get(img)