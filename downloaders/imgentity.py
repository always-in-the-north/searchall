class ImgEntity(object):

	wangluodizhi =""
	bendidizhi = ""
	kuozhanming = ""
	
	"""docstring for ClassName"""
	def __init__(self, arg = ""):
		super(ImgEntity, self).__init__()
		self.arg = arg

	def __str__(self):
		return 'ImgEntity info wangluodizhi: {}, bendidizhi: {}, kuozhanming: {}' \
			.format(self.wangluodizhi, self.bendidizhi, self.kuozhanming)

	def __repr__(self):
		return self.__str__()

