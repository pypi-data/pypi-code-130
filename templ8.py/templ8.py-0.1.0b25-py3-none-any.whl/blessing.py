import os
from pathlib import Path
import textile
import pypandoc
import time
import re
import pykami
import sys

class FileData:
	def __init__(self):
		self.path = Path("")


pextra = ["-f", "markdown-smart"]

TEMPL8_ASCII = """
	###																	
	###																  ###
	###																  ###		#####
###########		   ###												  ###	  ##	###
###########		#########	   ### ####    #####	  ### ######	  ###	 ##		 ###
	###		   ###	   ###	   ###################	  ############	  ###	 ##		####
	###		  ###		###    ###	  ####	  ####	  ###	   ####   ###	  ##   ####
	###		  #############    ###	   ###	   ###	  ###		###   ###	   #######
	###		  #############    ###	   ###	   ###	  ###	   ####   ###	 ####	 ##
  #######	  ###			   ###	   ###	   ###	  ############	  ###	####	   ##
	###		  ####		###    ###	   ###	   ###	  ##########	  ###	###		   ##
	###			##########	   ###	   ###	   ###	  ###			  ###	 ###	 ###
	##			  ######	   ###	   ###	   ###	  ###			  ###	   ####### 
	##												  ###
	#"""
	
# Misnomer: This is the default blogbase
DEF_BASEHTML_CONTENT = """PAGETITLE=##TITLE##
-BEGINFILE-
h2. ##TITLE##

^##AUTHORS## - ##TAGS## - ##DATE##^

##CONTENT##

-BEGININDEX-
h2. "##TITLE##":##LINK##

^##AUTHORS## - ##TAGS## - ##DATE##^

##INTRO##
-BEGININDEX-
PAGETITLE=Blog"""

DEF_INPUT = "input"
DEF_OUTPUT = "output"
DEITY_PATH = ".d8y"
DEF_BASEHTML_PATH = "base.html"
DEF_REPLACE_PATH = ".repl8ce"


# Checks if a directory exists and make it if not
def makedir(path, warning = ""):
	if not os.path.exists(path):
		if warning != "":
			print("WARNING: " + warning)
		os.mkdir(path)


# Processes the repl8ce of a header
def mod_replaces(input_replaces, header, file_data):
	# These variables are used for multiline keys
	current_multikey = "" # The current key being edited
	multiline = False
	
	for i in header.split("\n"):
		# Split it in the single line way
		keyval = [i]
		if not multiline:
			keyval = i.split("=", 1)
		# If we're not processing multilines, and the current line is single line, set key
		if len(keyval) == 2 and not multiline:
			input_replaces[keyval[0]] = keyval[1].replace("\\n", "\n")
		# If it's not a valid single line
		elif len(keyval) == 1:
			# If it's a valid multiline, start a new multiline tag
			if keyval[0].startswith(";;"):
				multiline = True
				current_multikey = keyval[0].replace(";;", "", 1)
				input_replaces[current_multikey] = ""
			# If it's not, continue the current multiline
			elif multiline:
				input_replaces[current_multikey] += keyval[0] + "\n"
			elif not keyval[0] == "":
				raise Exception("what")
	
	new_input_rel = input_replaces.copy()
	for i in new_input_rel:
		if i.startswith("TX-"):
			input_replaces[i.lstrip("TX-")] = parse_content(input_replaces[i], ".textile", file_data)
		elif i.startswith("MD-"):
			input_replaces[i.lstrip("MD-")] = parse_content(input_replaces[i], ".md", file_data)
		elif i.startswith("KM-"):
			input_replaces[i.lstrip("KM-")] = parse_content(input_replaces[i], ".km", file_data)


def parse_content(content, ext, file_data):
	if ext == ".textile":
		return textile.textile(content)
	elif ext == ".md":
		return pypandoc.convert_text(content, "html5", format="md", extra_args=pextra)
	elif ext == ".km":
		val = pykami.parse(content)
		while val[1].find("\n\n") != -1:
			val[1] = val[1].replace("\n\n", "\n")
		if val[1] != "\n" and val[1] != "":
			print(f"[KAMI WARNING] In {file_data.path}: " + val[1])
		return val[0]
	else:
		raise Exception("Can't recognize the extension in " + os.join(subdir, file))
		return ""

	
ifkey_start = "$$IF_"
ifnkey_start = "$$IF!"
forkey_start = "$$FOR_"
fkey_end = "$$END$$"


class Token:
	def __init__(self, type, start, end):
		self.end = end
		self.type = type
		self.start = start
	def text(self, input_base):
		return input_base[self.start:self.end]
	def __repr__(self):
		return f"[ C: {self.start} - {self.end} T: {self.type} ]"
	def __eq__(self, other):
		return (self.end == other.end and self.start == other.start)

tokens = [
	("if", re.compile(r"(?<!\\)\$ ?IF (NOT )?[A-Z0-9-_%]+( ?\$?)")),
	("plug", re.compile(r"(?<!\\)\$ ?PLUG [A-Z0-9-_%.]+( ?\$?)")),
	("pl", re.compile(r"(?<!\\)\$ ?PL [A-Z0-9-_%.]+( ?\$?)")),
	("for", re.compile(r"(?<!\\)\$ ?FOR [A-Z0-9-_%]+ [A-Z]( ?\$?)")),
	("end", re.compile(r"(?<!\\)\$ ?END( ?\$?)")),
	("tag", re.compile(r"(?<!\\)\#\#[A-Z0-9-_%]+ ?(\#\#)?")),
]

openers = ["if", "for", "plug"]


def get_charpos(i, str):
	lines = str.splitlines()
	last_pos = 0
	for j in range(len(lines)):
		last_pos += len(lines[j])
		if last_pos > i:
			last_pos -= len(lines[j])
			return (j + 1, i-last_pos-j+1)


def parts(input_base, file_data):
	all_lexes = []
	last_end = 0
	while True:
		earliest = Token("nil", -1, -1)
		for name, gex in tokens:
			x = gex.search(input_base, last_end)
			if x and (x.span()[0] < earliest.start or earliest.type == "nil"):
				earliest = Token(name, x.span()[0], x.span()[1])
		
		if earliest.type != "nil":
			all_lexes.append(Token("put", last_end, earliest.start))
			all_lexes.append(earliest)	
			last_end = earliest.end
		else:
			all_lexes.append(Token("put", last_end, len(input_base)))
			break
	
	# Syntax error checking
	opens = []
	for i in all_lexes:
		if i.type in openers:
			opens.append(i)
		elif i.type == "end":
			if opens == []:
				errpos = get_charpos(i.start, input_base)
				print(f"ERROR: UNEXPECTED END OF BLOCK AT ({errpos[0]}; {errpos[1]}) IN {file_data.path}")
				sys.exit()
			else:
				opens.pop(-1)
	if opens != []:
		errpos = get_charpos(opens[-1].start, input_base)
		print(f"ERROR: UNCLOSED {opens[-1].type.upper()} AT ({errpos[0]}; {errpos[1]}) IN {file_data.path}")
		sys.exit()
	return all_lexes


def funkeys(input_base, keys, tokens, file_data, iter_variables = {}):
	out = ""
	iter = 0
	
	while iter < len(tokens):
		tok = tokens[iter]
		ttext = tok.text(input_base)
		
		# Replace all the %A iteration variables
		for i in iter_variables:
			ttext = ttext.replace("%"+i, str(iter_variables[i]))
			
		if tok.type == "put":
			out += ttext.replace("\\##", "##").replace("\\$", "$").replace("\\$", "$").replace("\n\n", "\n")
		if tok.type == "tag":
			tagley = ttext.replace("##", "").lstrip().rstrip()
			if tagley in keys and tagley != "CONTENT":
				out += keys[tagley]
		elif tok.type == "if":
			clex = ttext.replace("$IF", "").lstrip().rstrip()
			clex = clex.replace("$ IF", "").lstrip().rstrip()
			do = False
			if clex.startswith("NOT"):
				do = not do
				clex = clex.lstrip("NOT").lstrip()
			if clex in keys and keys[clex] != "":
				do = not do
			if not do:
				opens = 0
				for subtok in tokens[iter:]:
					if subtok.type in openers:
						opens += 1
					elif subtok.type == "end":
						opens -= 1
					if opens == 0:
						break
					iter += 1
		elif tok.type == "plug":
			clex = ttext.replace("$ PLUG", "").lstrip().rstrip()
			clex = clex.replace("$PLUG", "").lstrip().rstrip()
			clex = clex.replace("$", "").lstrip().rstrip()
			pluginpath = Path.home().joinpath("pl8g").joinpath(clex.lower()).joinpath("main.py")
			plugindir = Path.home().joinpath("pl8g").joinpath(clex.lower())
			opens = 0
			itc = iter+1
			body = ""
			for subtok in tokens[iter:]:
				if subtok.type in openers:
					opens += 1
				elif subtok.type == "end":
					opens -= 1
				if opens == 0:
					break
				itc += 1
			body = funkeys(input_base, keys, tokens[iter+1:itc], file_data, iter_variables)
			plugglobals = {
				'output': body,
				'plugdir': plugindir,
				'plugpath': pluginpath,
				'filepath': file_data.path,
				'repl8ce': keys,
			}
			exec(open(pluginpath, 'r').read(), plugglobals)
			out += plugglobals["output"]
			iter = itc-1

		elif tok.type == "pl":
			clex = ttext.replace("$ PL", "").lstrip().rstrip()
			clex = clex.replace("$PL", "").lstrip().rstrip()
			clex = clex.replace("$", "").lstrip().rstrip()
			pluginpath = Path.home().joinpath("pl8g").joinpath(clex.lower()).joinpath("main.py")
			plugindir = Path.home().joinpath("pl8g").joinpath(clex.lower())
			plugglobals = {
				'output': '',
				'plugdir': plugindir,
				'plugpath': pluginpath,
				'filepath': file_data.path,
				'repl8ce': keys,
			}
			exec(open(pluginpath, 'r').read(), plugglobals)
			out += plugglobals["output"]

		elif tok.type == "for":
			clex = ttext.replace("$ FOR", "").lstrip().rstrip()
			clex = clex.replace("$FOR", "").lstrip().rstrip()
			itervar = clex.split(" ")[1]
			clex = clex.split(" ")[0]
			opens = 0
			it2 = iter+1
			fit = 0
			for subtok in tokens[iter:]:
				if subtok.type in openers:
					opens += 1
				elif subtok.type == "end":
					opens -= 1
				if opens == 0:
					break
				it2 += 1
			while f"{clex}{fit}" in keys and keys[f"{clex}{fit}"] != "":
				out += funkeys(input_base, keys, tokens[iter+1:it2], file_data, {itervar: fit, **iter_variables})
				fit += 1
			iter = it2-1
		iter += 1
	return out


def into_html(content, keys, state, file_data):
	# By default, use the default base
	base = state.basehtml_content
	# Use a custombase if it's specified
	if "CUSTOMBASE" in keys:
		if os.path.exists(keys["CUSTOMBASE"]):
			base = open(keys["CUSTOMBASE"], "r").read()
		else:
			raise Exception(file_data.path + " uses a CUSTOMBASE that doesn't exist")
	
	# Put the content in the file
	base = base.replace("##CONTENT##", content)
	
	# Replace special keys
	base = base.replace("#!DATE!#", time.ctime(time.time()))
	
	# Tokenize for function keys and apply them
	tokens = parts(base, file_data)
	if len(tokens) != 0:
		base = funkeys(base, keys, tokens, file_data)
	
	return base


def full_parse(state, file_content, file_extension, file_headers, dir_replace, file_data):
	# Process repl8ce
	filerepl = state.replacements.copy()
	filerepl.update(dir_replace)
	mod_replaces(filerepl, file_headers, file_data)
	
	# Turn the content into HTML
	contents = parse_content(file_content, file_extension, file_data)
	
	# Put the content in the base HTML
	contents = into_html(contents, filerepl, state, file_data)
	
	return contents


def parse_keys(page, keys, file_data):
	base = page
	tokens = parts(base, file_data)
	if len(tokens) != 0:
		base = funkeys(base, keys, tokens, file_data)
	
	for key in keys:
		if key.startswith("TX-"):
			base = base.replace("##"+key+"##", parse_content(keys[key], ".textile", file_data))
		elif key.startswith("MD-"):
			base = base.replace("##"+key+"##", parse_content(keys[key], ".md", file_data))
		else:
			base = base.replace("##"+key+"##", keys[key])
	
	return base
