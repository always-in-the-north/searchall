from threading import Thread
import time
import queue

from providers.fzdm import Fzdm

from downloaders.downloader import DownLoader
from downloaders.imgentity import ImgEntity

from scheduleres.loggings import logger

_d = DownLoader()

def main():
	f = Fzdm()

	logger.debug('thread start ...')

	cron_thread = Thread(target=downloadthread, args=(f.download_queue, ))
	parse_thread = Thread(target=f.parse, args=())

	try:
		cron_thread.start()
		parse_thread.start()
		
		parse_thread.join()
		cron_thread.join()
		
	except (KeyboardInterrupt, SystemExit):
		logger.debug('catch KeyboardInterrupt, exiting...')
	finally:
		pass
	


def downloadthread(download_queue):
	_runflag = True
	try:
		while True:
			if _runflag == False:
				break
			try:
				item = download_queue.get(block = False)
			except queue.Empty as e:

				time.sleep(2)
				logger.debug('wait for download info 2 seconds')
				continue

			_d.get(item)
			download_queue.task_done()
	except (KeyboardInterrupt, SystemExit):
		_runflag = False
