from .Base import *
from .func import GetToken
from discord import Webhook as wh
import aiohttp


class webhook(object):
	def __init__(self, Id,Token,**kw):
		super(webhook, self).__init__()
		self.webhook_ = hook(Id,Token)
		self.Token    = self.webhook_.Token
		self.id       = self.webhook_.id
		self.__dict__.update(self.webhook_.data.data)
		self.username = kw.get("username", self.webhook_.data.data[ "name" ])
		self.avatar   = kw.get("avatar"  , self.webhook_.data.data["avatar"])
		self.discriminator = "0000"
	def get(self):
		return self.webhook_.data
	async def send_(self,*args,**kw):
		kw["username"]   = self.username
		kw["avatar_url"] = self.avatar
		async with aiohttp.ClientSession() as session:
			webhook = wh.partial(
				self.id,self.Token,
				session=session)
			return await webhook.send(*args,**kw)
	async def web(self):
		async with aiohttp.ClientSession() as session:
				self.webhook = wh.partial(
					self.id,self.Token,
					session=session)
				self.session = session
		return self
	async def Test(self):
		async with aiohttp.ClientSession() as session:
			webhook = wh.partial(
				self.id,self.Token,
				session=session)
			await webhook.send("Hello World!")
			print("Hello World!")
	async def send(self,*args,**kw):
		return await self.send_(*args,**kw)
class hiWebhook(webhook):
	def __init__(self, link,**kw):
		super(webhook, self).__init__(**self.__dict__)
		self.webhook_ = hook(*GetToken(link))
		self.Token    = self.webhook_.Token
		self.id       = self.webhook_.id
		self.username = kw.get("username", None)
		self.avatar   = kw.get("avatar", None)
		self.link     = self.webhook_.link
		self.discriminator = "0000"

class webhookIO(webhook):
	def __init__(self, username="Spidey Bot",avatar=None):
		self.webhook_ = hookIO(name=username,avatar=avatar)
		self.Token    = self.webhook_.Token
		self.id       = self.webhook_.id
		self.username = username
		self.avatar   = avatar
		self.link     = self.webhook_.link
		self.discriminator = "0000"
