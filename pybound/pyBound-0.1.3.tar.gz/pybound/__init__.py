__version__ = '0.1.3'

import sys, os
from time import sleep

def delete_line(num):
	CURSOR_UP_ONE = '\x1b[1A' 
	ERASE_LINE = '\x1b[2K' 
	for i in range(num):
    sys.stdout.write(CURSOR_UP_ONE) 
		sys.stdout.write(ERASE_LINE)
def clear():
	os.system('clear')
def slow_print(*strings, time = 0.045, sep = ' ', end = '\n', file = sys.stdout):	
	num = len(strings)
	for string in strings:
		string = str(string)
		for character in string:
			str(character)
			file.write(character)
			file.flush()
			sleep(time)
		num -= 1
		if num != 0:
			file.write(sep)
			file.flush()	
	file.flush()
	file.write(end)
	file.flush()
def wait(time = 1):
  sleep(time)