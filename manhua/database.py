import datetime
import os
from peewee import ForeignKeyField, CharField, AutoField, DateTimeField, BooleanField, FloatField, IntegerField, MySQLDatabase, SqliteDatabase

from playhouse.signals import Model

from manhua.config import get_config
from manhua.customexception import SqliteDbFilenotFoundError
_db = None


def create_connection() -> MySQLDatabase:
	"""
	create a database connection
	:rtype: MySQLDatabase
	"""
	global _db
	if _db:
		return _db
	else:
		# logger.debug('create new db connection')
		_db = MySQLDatabase(get_config("db_dbname"), user=get_config("db_user"),  password=get_config("db_password"),
							host=get_config("db_host"), port=get_config("db_port"))

		return _db

def create_connection_sqlite() -> SqliteDatabase:
	"""
	create a database connection
	:rtype: SqliteDatabase
	"""
	if(not os.path.exists(get_config('db_path_qiushibaike', './qiushibaike.db'))):
		raise SqliteDbFilenotFoundError("Sqlit db file not exists")

	return SqliteDatabase(get_config('db_path_qiushibaike', './qiushibaike.db'))


class BaseModel(Model):
	class Meta:
		database = create_connection()

class BaseModelSqlite(Model):
	class Meta:
		database = create_connection_sqlite()

def create_db_tables_sqlite(tables):
	db = create_connection_sqlite()
	db.create_tables(tables)


def create_db_tables():
	db = create_connection()
	db.create_tables([Manhua, ManhuaSub, ManhuaSetting])

class Manhua(BaseModel):

	class Meta:
		table_name = 'manhua_head'

	manhua_id = CharField()
	biaoti = CharField()
	zuixinhua = CharField()
	wangluodizhi = CharField()
	updatedate = DateTimeField(default=datetime.datetime.now)
	insetdate = DateTimeField(default=datetime.datetime.now)
	
	def set_value(self, m):
		self.manhua_id = m.manhua_id
		self.biaoti = m.biaoti
		self.zuixinhua = m.zuixinhua
		self.wangluodizhi = m.wangluodizhi


	# toString时用到的方法
	def __str__(self):
		return '[manhua info: biaoti: {}, manhua_id: {}, zuixinhua: {}, wangluodizhi: {}]' \
			.format(self.biaoti, self.manhua_id, self.zuixinhua, self.wangluodizhi)

	# 输出对象实例调用的方法
	def __repr__(self):
		return self.__str__()

class ManhuaSetting(BaseModel):

	class Meta:
		table_name = 'manhua_setting'

	key = CharField()
	value = CharField()

	def __str__(self):
		return '[manhua_setting info key: {}, value: {}]' \
			.format(self.key, self.value)

	def __repr__(self):
		return self.__str__()


class ManhuaSub(BaseModel):

	class Meta:
		table_name = 'manhua_sub_head'

	manhua_id = CharField()
	manhua_sub_id = CharField()
	biaoti = CharField()
	yeshu = CharField()
	wangluodizhi = CharField()
	wangyewangluodizhi = CharField()
	bendidizhi = CharField()
	length = IntegerField()
	lastModified = DateTimeField(default=None)
	updatedate = DateTimeField(default=datetime.datetime.now)
	insetdate = DateTimeField(default=datetime.datetime.now)
	
	def set_value(self, m):
		self.biaoti = m.biaoti
		self.manhua_id = m.manhua_id
		self.manhua_sub_id = m.manhua_sub_id
		self.yeshu = m.yeshu
		self.wangluodizhi = m.wangluodizhi
		self.wangyewangluodizhi = m.wangyewangluodizhi
		self.bendidizhi = m.bendidizhi
		self.length = m.length
		self.lastModified = m.lastModified
					
	def __str__(self):
		return '[manhua_sub info biaoti: {}, manhua_sub_id: {}, wangluodizhi: {}, bendidizhi: {}]' \
			.format(self.biaoti, self.manhua_sub_id, self.wangluodizhi, self.bendidizhi)

	def __repr__(self):
		return self.__str__()


class QiuShiBaiKeArticle(BaseModelSqlite):

	class Meta:
		table_name = 'qiushibaikearticle'

	articleId = CharField()
	articleType = CharField()
	articleUrl = CharField()

	content = CharField()

	imgBendi = CharField(default=None)
	imgWangluo = CharField(default=None)

	videoWangluo = CharField(default=None)

	articleFunny = CharField()
	articleComment = CharField()

	updatedate = DateTimeField(default=datetime.datetime.now)
