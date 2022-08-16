"""
from DisWebhooker.command import BaseCommand
import inspect
import json
BC = BaseCommand(prefix="?")

stringCommand = "?say yo mama is fat" #:(

####### func
def lister(func):
	argsspec = inspect.getfullargspec(func)
	_ = []
	_ += argsspec.args
	if argsspec.varargs:
		_ += "*"
		_ .append ( argsspec.varargs )
	if _:
		print(_)
		print(argsspec)

	return _,argsspec.defaults

def passer(func,defaults,*args,**kw):
	print(vars())
	if not args and defaults is not None:
		args+=defaults
	return func(*args,**kw)


def foo(arg1,*arg2,**args):
	print(vars())
	print(arg1,*arg2)
commands = {}
commands["say"] = foo
#list(inspect.signature(foo).parameters)
EvalArgs,defaults = lister(foo)
_ = BC.process_command(command=stringCommand,EA=EvalArgs) # EA: Eval Args

var = tuple(_["VARIABLES"].values())
var = ()
print(json.dumps(_,indent=4))

passer(commands[_["RETURNS_GET"][1]],defaults,*var)


exit()
"""

########################## import #########################
from DisWebhooker.commands import commands as webcommands
from DisWebhooker.bot import Bot
from DisWebhooker.bot import hibot
from DisWebhooker.webhook import webhook
from DisWebhooker.webhook import hiWebhook
from DisWebhooker.mkrTree import Tree
from DisWebhooker.func import CreateTree as CW
from DisWebhooker.func import Getavatar
from DisWebhooker.func import GetToken
import discord
from discord.ext import commands
##########################  exec  ###########################


class hibot(hibot):
	async def webhookHandler(self,webhookobj,message):
		_,obj = self.webhookObject(webhookobj)
		data = obj.webhook.get().data
		try:
			kw = {"name":data["name"],"avatar":Getavatar(data["id"],data["avatar"])} if data["avatar"] is not None else {"name":data["name"],"avatar":None}
		except TypeError as e:
			if str( e ) == "can only concatenate str (not \"NoneType\") to str":
				kw = {"name":data["name"],"avatar":None}
			else:
				raise e
		channel = message.channel
		if not isinstance(channel,discord.TextChannel):
			print("get a message from non-TextChannel {0}".format(message))
			return None
		if list(await channel.webhooks()) != []:
			for web in await channel.webhooks():
				if web.url:
					w_w = hiWebhook(web.url,username=kw["name"],avatar=kw["avatar"])
					break
				else:
					web = await channel.create_webhook(name="webhooker-webhook")
					w_w = hiWebhook(web.url,username=kw["name"],avatar=kw["avatar"])
					break
		else:
			web = await channel.create_webhook(name="webhooker-webhook")
			w_w = hiWebhook(web.url,username=kw["name"],avatar=kw["avatar"])
		_webhook_ = obj.webhook
		obj.webhook = w_w
		obj.webhook.extra_events = {}
		try:
			processing = await obj.process_command(message,message.content)
			obj.webhook = _webhook_
			return processing
		except Exception as e:
			obj.webhook = _webhook_
			raise e
		return None



intents = discord.Intents.all()

webhookerBot = Bot(command_prefix="?")#,setuped=True)
webhookerBot2= Bot(command_prefix="#",setuped=True,username="beepboop")
#webhookerBot.setup(*GetToken("https://discord.com/api/webhooks/985899408371613726/KE8yMRriu2Tz1d0NC-xN7qfmWoZiVK3dua15EEhqByYFplo2NkaFSgkCCOXlMPFj2Ejv"))
print("setuped",webhookerBot2.user)
print("setuped",webhookerBot.user)
webhooks = [CW(webhookerBot,name=webhookerBot.user),CW(webhookerBot2,name=webhookerBot2.user)]



client = hibot(webhooks=webhooks,command_prefix = "!",intents=intents, guild_subscriptions=True)

# bot 1
@webhookerBot.event
async def on_raw_message_delete(bot,message):
	print(message)
	print(bot)
@webhookerBot.event
def on_ready():
	print('Logged on as {0}!'.format(client.user))



@webhookerBot.command(name="say",description="make the bot say anything :) 'Hello World'")
async def test_webhook(self,ctx,*arg):
	await self.send(*arg)

@webhookerBot.command(name="hi",description="say 'Hello, World!'")
async def Hello_World(self,ctx):
	await self.send("Hello, World!")

# bot 2
@webhookerBot2.command(name="hi",description="say 'Hello, World!'")
async def Hello(self,ctx):
	await self.send("Hello, World!")

@webhookerBot2.command(name="time",description="give you the time")
async def Hello_World(self,ctx):
	import time
	await self.send(f"the time right now is {time.strftime('%I:%M:%S %Y/%m/%d (%z)')}")
# main bot
@client.command(name="test")
async def ping(ctx: commands.Context):
		await ctx.send(f'Pong! {round(client.latency * 1000)}')

@client.command()
async def pong(ctx):
    await ctx.send('**ping**')
@client.event
async def on_invite_create(*args,**kw):
	print(args,kw)
@client.event
async def on_socket_raw_receive(payload):
	print(payload)
@client.event
async def on_socket_raw_receive(payload):
	print(payload)
@client.event
async def on_socket_response(msg):
	print(msg)
from DisWebhooker.func import GetToken
#webhookerBot.setup("975426616635326574","x_8old17oslbgds-wLFxZjfQTRXsb-JmrbpfTlymfpmJr7e7_xc8uJZod1deWSb8VbEp")
#webhookerBot.setup(*GetToken("https://discord.com/api/webhooks/985899408371613726/KE8yMRriu2Tz1d0NC-xN7qfmWoZiVK3dua15EEhqByYFplo2NkaFSgkCCOXlMPFj2Ejv"))
webhookerBot.setup(*GetToken("https://discord.com/api/webhooks/984528168172003388/XSNVwnLgwc4moe6oC1KcHqJD0JJ9qKu8Img1MnfnIpDNiFiytXY6-WPDkKtQ1qclF-rX"))
client.run("OTkxOTAyMjU1ODgyMTk1MDY0.Gzm42-.6Tqokhn2jt82u-TqLy0KVd6Q4zzN4_BYO6gur0")