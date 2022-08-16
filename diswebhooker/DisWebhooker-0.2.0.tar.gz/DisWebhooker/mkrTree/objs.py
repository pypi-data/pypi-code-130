
class Data(object):
	def __init__(self,data,name):
		super(Data, self).__init__()
		self.data = data
		self.name = name
	def __repr__(self):
		return f"<Data(data=\"{self.name}\")>"
