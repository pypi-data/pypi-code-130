from VbeeLogger import constant
import datetime, json
class Logging():

	def __init__(self, env, product, service, name, custom={}):
		self.env = env
		self.product = product
		self.service = service
		self.name = name
		self.custom = custom

	def get_time(self):
		return datetime.datetime.now().isoformat()[:-3]+"Z"

	def create_msgjson(self, mess, custom={}):
		return json.dumps({
			constant.ENV_KEY: self.env,
			constant.PRODUCT_KEY: self.product,
			constant.SERVICE_KEY: self.service,
			constant.CLASS_KEY: self.name,
			constant.CUSTOM_KEY: custom,
			constant.MESSAGE_KEY: mess
		}, ensure_ascii=False)

	def print(self, mess:str, levelname:str, custom={}):
		print(f"[{self.get_time()}] [{levelname}] - - {self.create_msgjson(mess, custom)}")

	def info(self, mess:str, custom={})->None:
		self.print(mess, constant.INFO, custom)

	def error(self, mess:str, custom={})->None:
		self.print(mess, constant.ERROR, custom)

	def warning(self, mess:str, custom={})->None:
		self.print(mess, constant.WARNING, custom)

	def warn(self, mess:str, custom={})->None:
		self.print(mess, constant.WARNING, custom)
		
	def debug(self, mess:str, custom={})->None:
		self.print(mess, constant.DEBUG, custom)
		
if __name__ == '__main__':
	logger = Logging("test_product","test_service","test_name")
	logger.info("hello")
