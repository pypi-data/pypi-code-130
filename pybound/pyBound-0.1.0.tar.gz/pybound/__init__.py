__version__ = '0.1.0'

import sys, os, time
def dl(num):
	CURSOR_UP_ONE = '\x1b[1A' 
	ERASE_LINE = '\x1b[2K' 
	for i in range(num):
		sys.stdout.write(CURSOR_UP_ONE) 
		sys.stdout.write(ERASE_LINE)
def clear():
	os.system('clear')
def slowprint(tamt, s):
	for c in s + '\n':
		sys.stdout.write(c)
		sys.stdout.flush()
		time.sleep(tamt)
