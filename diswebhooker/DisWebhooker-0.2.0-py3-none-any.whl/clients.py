from discord.ext import commands
from .errors import InvalidArgumentError
from .errors import InvalidTreeError
from .webhook import webhook
from .mkrTree.tree import Tree



class Clients(commands.Bot):
	def __init__(self, webhooks:Tree,*args,**kw):
		super(Clients,self).__init__(*args,**kw)
		self.webhooks = webhooks
		if not isinstance(webhooks,Tree) and not isinstance(webhooks,list):
			raise InvalidArgumentError("webhooks must be \"Tree\" not \"%s\"" % (webhooks.__class__.__name__))
		else:
			if not isinstance(webhooks,list):
				if webhooks.name.lower() != "webhooks":
					raise InvalidTreeError("webhooks are not found in %s" % webhooks)
			else:
				if isinstance(webhooks,Tree):
					if webhooks.children == []:
						raise InvalidArgumentError("There's no webhooks in %s" % (webhooks))
					return
				elif isinstance(webhooks,list):
					if webhooks == []:
						raise InvalidArgumentError("There's no webhooks in %s" % (webhooks))
					self.webhooks = Tree("webhooks")
					for webhook in webhooks:
						if isinstance(webhook,Tree):
							self.webhooks.append(webhook)
						else:
							raise InvalidTreeError("webhook must be \"Tree\" not \"%s\":%s" % (webhook.__class__.__name__,webhook))
					del webhook
				else:
					raise InvalidArgumentError("webhooks must be \"Tree\" not \"%s\"" % (webhooks.__class__.__name__))
		return

	def webhookObject(self,webhookobj):
		webhookobj = webhookobj.data.data
		if isinstance(webhookobj["obj"],webhook):
				raise InvalidTreeError("webhook must be \"webhook\" not \"%s\":%s" % (webhookobj["obj"].__class__.__name__,webhookobj))
		else:
			return webhookobj["name"], webhookobj["obj"]
	commands.Cog.listener()
	async def on_message(self, message):
		if message.author.bot:
			return
		asyncio.create_task(self.webhooks_handler(message))
		return await self.process_commands(message)