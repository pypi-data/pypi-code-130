from urllib.request import (urlopen, Request,)
from json import (loads, dumps,)
from requests import (request,)


class Methods(object,):
	def __init__(self, token,):
		self.token = token

	def createMethod(self, method, json_data, files = None,):
		if files == None:
			return loads(urlopen(Request(url = 'https://eitaayar.ir/api/{}/{}'.format(self.token, method,), headers = {'Accept': 'application/json',}, data = dumps(json_data,).encode())).read().decode('utf-8',),)

		else:
			return request('POST', url = 'https://eitaayar.ir/api/{}/{}'.format(self.token, method), data = json_data, files = files,).json()