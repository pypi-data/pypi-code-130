from mkrTree  import *
from .command import *
from .errors  import CommandError
from .errors  import EmptyCommand
import asyncio





class Remove(Remove):
	def removeIt(self):
		if self.tree.children == []:
			raise ValueError(f"can't reomve child with an empty tree : {self.tree}")
		children = self.tree.children
		for child_ind in range(len(children)):
			child = children[child_ind]
			if child == self.name:
				del children[child_ind]
				return children
		raise TypeError(f"tree is not defined : {children}")


_default_command = None


class command(object):
	"""docstring for command"""
	def __init__(self,func,name=None,**kw):
		super(command, self).__init__()
		self.description = kw.get("description","")
		self.description = kw.get("help",self.description)
		name = name
		self.name = func.__name__ if name is None else name
		self.func = func
		self.indent = kw.get("indent",1)
		self.repr_ = kw.get("sep"," ")+self.name+((" "*(self.indent+1))[len(name):]+":"+self.description if self.description else "")
		self.kw = kw

	def function(self,start=None,end=None,*args,**kw):
		# do something befoer the start of the func
		if start is not None: start(*args,**kw)
		ret = self.func(*args,**kw)
		# do something afther the start of the func
		if start is not None: end(*args,**kw)
	def __repr__(self):
		return self.repr_



class commands(object):
	"""docstring for commands"""
	def __init__(self,command_prefix,help_command=_default_command,tree=None):
		super(commands, self).__init__()
		self.command_prefix = command_prefix
		self.tree           = tree if tree is not None else Tree
		self.commandsTree   = self.tree("commands")
		self.indent = 0
		self.commands = {}
		self.help_command = help_command
	def add_command(self, func,name=None,**kw):
		name = name if name is not None else func.__name__
		if len(name) > self.indent: self.indent = len(name); self.update_commands(len(name))
		kw["indent"]        = self.indent
		kw["sep"]           = kw.get("sep","")
		createdObj          = command(func,name=name,**kw)
		commandsHelp        = self.tree(name=str(createdObj),obj=createdObj, parent=self.commandsTree)
		self.commands[name] = commandsHelp
	def remove_command(self,name=None,**kw):
		name = name if name is not None else (kw.get("func").__name__ if kw.get("func") is not None else None)
		if name is None:
			raise CommandError("Name is None")
		Remove(self.commandsTree,self.commands[name]).removeIt()
		if len(name) < self.indent: self.indent = self.biggestIndent()
		if kw.get("update ",True): self.update_commands(len(name))
	def replace_command(self, func,name=None,**kw):
		self.remove_command(name,update=False,**kw)
		self.add_command(func,name,**kw)
	def existing_command(self,name):
		try:
			cmd = self.commands[name]
			return cmd,False
		except KeyError as e:
			return None,True
	def biggestIndent(self):
		newindent = 0
		oldindent = 0
		ct = self.commandsTree
		for ind in range(len(ct.children)):
			obj  = ct.children[ind].data.data["obj"]
			name = obj.name
			newindent = len(name)
			if newindent > oldindent:
				oldindent = newindent
		return oldindent
	def display_(*args,**kw):
		return treeRander(*args,**kw).displayTree(self.commandsTree)
	def display(*args,**kw):
		print(self.display_(*args,**kw))
	def sorted(self,**kw):
		D_ = {}
		for key in sorted(self.commands,**kw): D_[key] = self.commands[key]
		self.commands = D_
		self.commandsTree.sorted(change=True)
		return D_
	def update_commands(self,indent):
		ct = self.commandsTree
		for ind in range(len(ct.children)):
			obj  = ct.children[ind].data.data["obj"]
			name = obj.name
			func = obj.func
			self.replace_command(func,name,**obj.kw)
	def help_message(self):
		string = treeRander().displayTree(self.commandsTree)
		return string
	def call_command(self,name,*args,**kw):
		cmd, err = self.existing_command(name)
		if err:
			raise CommandError(f"Command \"{name}\" is not defined")
		else:
			func = cmd.data.data["obj"].func
			return func(*args,**kw)
	async def awaitit_command(self,name,*args,**kw):
		cmd, err = self.existing_command(name)
		if err:
			raise CommandError(f"Command \"{name}\" is not defined")
		else:
			func = cmd.data.data["obj"].func
			return asyncio.create_task(func(*args,**kw))
	def get_func(self,name):
		cmd, err = self.existing_command(name)
		if err:
			if name : raise CommandError(f"Command \"{name}\" is not defined")
			else: raise EmptyCommand(f"Command is emtpy")
		else:
			func = cmd.data.data["obj"].func
			return func

"""
			def foo():
				print("Hello foo!")
			(self.add_command(foo,name="foo",description="just random command"))
			#(self.remove_command(name="__default_command__",description="just random command"))
			self.call_command("foo")		
"""