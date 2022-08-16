from .func   import CreateWebLink
from .func   import Request
from .errors import InvalidWebhook
from .objs   import Data
from .objs   import Link


class hook(object):
	"""docstring for hook"""
	def __init__(self, Id,Token):
		super(hook, self).__init__()
		self.Token = Token
		self.id    = Id
		self.link  = CreateWebLink(self.id,self.Token)
		self.data = Data(self.Request().json(),"webhook-data")
	class Error(object):
		def __init__(self,Error,message):
			self.Error   = Error
			self.message = message
	def Request(self):
		info = f"{self.id}/'{self.Token}'"
		e  = (InvalidWebhook,f"Invalid Id/Token :: {info}")
		rq = Request(self.Error(*e),self.link.url)
		return rq
	def __repr__(self):
		return f"<hook({self.__dict__})>"
class hookIO(hook):
	def __init__(self,name="Spidey Bot",avatar=None,**kw):
		super(hook, self).__init__(**kw)
		self.Token = None
		self.id    = None
		self.link  = None
		self.data  = Data({"name":name,"avatar":avatar,"id":"","channel_id":"0"},"webhook-data")
		self.avatar= avatar
		self.name  = name

class Webhook(object):
	def __init__(self, Id,Token):
		super(Webhook, self).__init__()
		webhook      = hook(Id,Token)
		self.webhook = webhook
		self.Token   = webhook.Token
		self.id      = webhook.id


