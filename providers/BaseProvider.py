

class BaseProvider(object):
	"""docstring for ClassName"""
	def __init__(self, arg):
		super(BaseProvider, self).__init__()
		self.arg = arg		
		self.headersFlag = True
		self.proxiesFlag = True

	def __str__(self):
		return self.__class__.__name__

	def parse():
		pass



