from bs4 import BeautifulSoup

from providers.BaseProvider import BaseProvider

from scheduleres.worker import Worker
from scheduleres.database import QiuShiBaiKeArticle
from scheduleres.database import create_db_tables_sqlite
from scheduleres.loggings import logger

import re
import pysnooper
import schedule
import time 

class QiuShiBaiKe(BaseProvider):
	def __init__(self):
		self._worker = Worker(pFlag = True)

		# db connect
		create_db_tables_sqlite([QiuShiBaiKeArticle])

	def schedulerparse(self):
		self.parse()
		
		schedule.every(12).hours.do(self.parse)

		while True:
			try:
				schedule.run_pending()

				time.sleep(60)

			except (KeyboardInterrupt, InterruptedError):
				logger.info('Stopping python scheduler')
				break

	# @pysnooper.snoop()
	def parse(self):
		# 热图
		root_urls = [("https://www.qiushibaike.com/" + y + "/page/" + str(x) + "/", y) for y in ['imgrank', 'video', 'text'] for x in range(1,14) ]
		for url in root_urls:
			soup = self._worker.get_html(url = url[0])
			content = soup.find(class_ = "col1")
			articles = content.find_all(id=re.compile(r"qiushi_tag_\d+"))

			for article in articles:
				q = QiuShiBaiKeArticle()
				basic_query = q.select().where(QiuShiBaiKeArticle.articleId == article["id"])

				if basic_query.count() == 0:
					q.articleId = article["id"]
					q.articleType = url[1]
					q.articleUrl = article.find("a", class_="contentHerf")["href"]

					imgdiv = article.find("div", class_="thumb")
					if not imgdiv == None :
						q.imgWangluo = imgdiv.find("img")["src"]

					videodiv = article.find("video")
					if not videodiv == None :
						q.videoWangluo = videodiv.source["src"]

					q.content = article.find("div", class_="content").span.string
					
					statsdiv = article.find("div", class_="stats")
					q.articleFunny = statsdiv.find("span", class_="stats-vote").i.string
					q.articleComment = statsdiv.find("span", class_="stats-comments").i.string

					q.save()
					logger.info('info update successfully.')
				else:
					logger.info('info exsits.')



