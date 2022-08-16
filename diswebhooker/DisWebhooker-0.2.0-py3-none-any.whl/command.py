from discord.ext.commands.view import StringView


class String(str):
	def split(content):
		c = content.split(" ")
		if c[0]: return c
		else: del c[0]
		return c
	def add(*,value,string):
		return string+value
	def ToStr(D_):
		return ("".join(D_["GetCmdArgs"]["RETURNS_GET"])\
		+ "".join([" "+(D_["evalArgs"]["VARIABLES"][key]) for key in D_["evalArgs"]["VARIABLES"].keys()]))
	def ToList(D_,split=" "):
		return String.ToStr(D_).split(split)
	def get_word(Word):
		return StringView(Word).get_word()
	def get_word_arg(Word,split="",index=0):
		return Word.split(split)[index]
	def split_(li):
		_ = [""," "]; ThisList = li[:]
		for I,O in enumerate(li):
			if O in _ or not O: ThisList.remove(O)
		return ThisList
	def chacks(string):
		return " ".join(String.split_(string.split(" ")))
	def read(string,n):
		return StringView(string).read(n)
	def display(text ,/, border="-", width=50):
		return f" {text} ".center(width,border)

class Basicommand(object):
	"""docstring for Basicommand"""
	def __init__(self, **Options):
		super(Basicommand, self).__init__()
		self.strip_after_prefix = Options.get('strip_after_prefix',False)
		self.prefix = Options.get('prefix', None)
		if self.prefix is None: 
			raise TypeError("missing option 'prefix'")

	def GetCmd_(self,command=""):
		view = StringView(command)
		commandName = view.buffer
		prefix = self.prefix

		if isinstance(prefix, str):
			if not view.skip_string(prefix):
				return commandName
		else:
			try:
				if origin.content.startswith(tuple(prefix)):
					invoked_prefix = discord.utils.find(view.skip_string, prefix)
				else:
					return commandName
			except TypeError as error:
				if not isinstance(prefix, list):
					raise TypeError(f"prefix must be a string or a list of strings, not {prefix.__class__.__name__}")

				for value in prefix:
					if not isinstance(value, str):
						raise TypeError(f"iterable [Command_Prefix] or list returned from prefix "\
							f"must contain only strings, not {value.__class__.__name__}")
		if self.strip_after_prefix:
			view.skip_ws()
		commandName = view.get_word()
		return (prefix,commandName)
	def Get_(self, *,view):
		return view.get_word()
	def GetCmd(self,command):
		view = StringView(command)
		commandName = view.buffer
		prefix = self.prefix

		if isinstance(prefix, str):
			if not view.skip_string(prefix):
				return (view,command)
		else:
			try:
				if origin.content.startswith(tuple(prefix)):
					invoked_prefix = discord.utils.find(view.skip_string, prefix)
				else:
					return (view,command)
			except TypeError as error:
				if not isinstance(prefix, list):
					raise TypeError(f"prefix must be a string or a list of strings, not {prefix.__class__.__name__}")
				for value in prefix:
					if not isinstance(value, str):
						raise TypeError(f"iterable [Command_Prefix] or list returned from prefix"\
							f" must contain only strings, not {value.__class__.__name__}")
		if self.strip_after_prefix:
			view.skip_ws()
		return (view,command)

	def GetCmdArgs(self,Returns_GetCmd,command):
		prefix = self.prefix
		self.prefix = ("".join([item for item in Returns_GetCmd]))
		_ = self.GetCmd(command)
		self.prefix = prefix
		s = _[0].buffer
		sreq = (String.read(s,len(self.prefix))) == self.prefix
		srneq = (String.read(s,len(self.prefix))) != self.prefix
		#print(f"""{(String.read(s,len(self.prefix)))} !=/== {self.prefix} "\
		#"==: {sreq} ---> return {(_,Returns_GetCmd,command)}\n!=: {srneq} ---> return {(_,("",""),command)}""")
		if   sreq:	return (_,Returns_GetCmd,_[0].read_rest())
		elif srneq:	return (_,("",""),_[0].read_rest())
		else: raise TypeError(f"else stm been active if:{sreq} elif:{srneq}") #this stm mustn't get active

	def evalArgs_(self, EA,*, args):
		if not isinstance(EA,list): raise TypeError(f"excepted a list but get {EA.__class__.__name__}")
		#if len(EA)<=0: raise TypeError(f"excepted items from the list but get none items : list len ({len(EA)})")
		args = list((args))
		string = ''
		Variables = {}
		Variables__ = []
		ind = None
		point = 0
		for index,value in enumerate(EA):
			if not isinstance(value,str):
				raise TypeError(f"value:EA[{index}] must be a string, not a {value.__class__.__name__}")
			elif value == "*":
				point = 1
				#Variables[EA[index+1]] = args[index]
			elif point == 1:
				li = args[len(Variables)::]
				Variables[EA[index]] = " ".join([str(st) for st in li])
				D__ = (EA[index] , ([str(st) for st in li]),)
				Variables__.append(D__)
				point = -1
				try: D__[EA[index+1]]
				except IndexError: break
			else:
				if point != -1:
					try: Variables[EA[index]] = args[index]
					except IndexError: Variables[EA[index]] = ''
					try: D__ = tuple((EA[index] , args[index]))
					except IndexError: D__ = tuple((EA[index] , ''))
					Variables__.append(D__)

		return Variables,Variables__

	def evalArgs(self, EA,*, args):
		return self.evalArgs_(EA=EA,args=args)[0],None


class BaseCommand(Basicommand):
	"""docstring for Basicommand"""
	def __init__(self, **Options):
		super(Basicommand, self).__init__()
		self.strip_after_prefix = Options.get('strip_after_prefix',False)
		self.prefix = Options.get('prefix', None)
		self.prefixIsEmpty = Options.get('prefixIsEmpty',False)
		self.Options = Options
		if self.prefix is None: 
			raise TypeError("missing option 'prefix'")
		elif self.prefix == "":
			self.prefixIsEmpty = True

	class Basicommand(Basicommand):
		pass

	def ValueRaiser(self,cls ,VariableName):
		raise ValueError(f"missing variable for [{cls.__name__}] :: Variable Name ({VariableName})")
	def Chacker(self,cls,Name,Value):
		if     Value    is    None: self.ValueRaiser(cls,Name)
		return Value
	def process_command_(self, **options):
		BC                       =  self.Basicommand
		command                  =  self.Chacker(BC,"command",options.get("command", None))
		EA                       =  self.Chacker(BC,"EA",options.get("EA", None))
		BC                       =  self.Basicommand(**self.Options)
		COMMAND,SELFCOMMAND      =  BC.GetCmd(command=command)
		STRINGVIEW               =  BC.Get_(view=COMMAND)
		_,RETURNS_GET,CONTENT    =  BC.GetCmdArgs(Returns_GetCmd=(self.prefix,STRINGVIEW),command=command)
		VARIABLES,VARIABLES__    =  BC.evalArgs_(EA = EA,args=String.split(CONTENT))
		D_ = {
		"GetCmd"    :  {
					"COMMAND"     : (COMMAND)  ,
					"SELFCOMMAND" : SELFCOMMAND
						},
		"GetCmdArgs":  {

					"RETURNS_GET" : RETURNS_GET,
					"CONTENT"     : CONTENT
						},
		"evalArgs"  :  {
					"VARIABLES"   : VARIABLES,
					"VARIABLES_"  : VARIABLES__
						},
		"procescomand":{
					"SELFCOMMAND" : SELFCOMMAND,
					"VARIABLES"   : VARIABLES  ,
					"RETURNS_GET" : RETURNS_GET, 
					"CONTENT"     : String.chacks(CONTENT),
					"CONTENTSPLIT": String.split(CONTENT)
						}
			  }
		return D_
		#["GG","__name__","0__class__0","1__class__1","2__class__2","3__class__3","4__class__4"]
	def process_command(self, **options):
		return self.process_command_(**options)["procescomand"]
