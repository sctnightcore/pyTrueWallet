class TruewalletException(Exception):
	def __init__(self, code, data):
		super(TruewalletException, self).__init__("[{}] {}".format(code, data))
		self.code = code
		self.data = data