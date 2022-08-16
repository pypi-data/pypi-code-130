from requests.api import request
from .mkrTree     import Tree
from .objs        import *
class GetTokenFailed(Exception):
	pass


def Request(self,url,method="GET",headers=None,payload=None):
		rq = request(
			method, url,
			headers = headers, params=payload)
		if rq.ok:
			return rq
		else:
			raise self.Error(self.message)
def _GetToken(url):
	rq = request(
		"GET", url
		)
	data = rq.json()
	if rq.ok:
		try:
			data["id"],data["token"]
			return (data)
		except Exception as e:
			raise GetTokenFailed("Get webhook token failed (:) Exception: \"%s: %s\"\nthe unexpected data:%s" % 
					(e.__class__.__name__, e, data))
	else:
		raise GetTokenFailed("Get webhook token failed (:) Exception: 'is ok?':%s, 'code': %s" % 
		(rq.ok, data))

def GetToken(url):
	data = _GetToken(url)
	return (data["id"],data["token"])
def CreateTree(webhook,*,name="webhook",**kw):
	return Tree(name,obj=webhook,**kw)
def CreateWebLink(id,token):
	return Link("discord.com/api/webhooks",
			f"https://discord.com/api/webhooks/{id}/{token}")
def Getavatar(Id,avatarId):
	return "https://cdn.discordapp.com/avatars/"+Id+"/"+avatarId+".webp"