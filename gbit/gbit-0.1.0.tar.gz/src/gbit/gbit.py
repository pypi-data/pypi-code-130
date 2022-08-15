#!/usr/bin/env python3

from os import path, listdir
import sys
from importlib import import_module

if len(sys.argv) != 2:
	sys.exit(2)

gtfobin = sys.argv[1]
dir_path = path.dirname(path.realpath(__file__)) # get the path to the current directory
binaries = listdir(dir_path) # get the modules

if gtfobin.lower()+".py" not in binaries: # check if the requested binary is in the modules
	print(f"{gtfobin} unavailable.")
	sys.exit(1)

module = import_module(f"{gtfobin}") # load the module
print(module.gtfobin)