__version__ = '0.2.2'

import sys, os
from time import sleep

def delete_line(num = 1):
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
      file.write(character)
      if string.startswith("\033") == False:
        file.flush()
        sleep(time)
    num -= 1
    if num != 0 or strings[len(strings)-num-1].startswith("\033") == False:
      file.write(sep)
      file.flush()	
  file.flush()
  file.write(end)
  file.flush()
def wait(time = 1):
	sleep(time)
def rgb(r, g, b):
		return "\033[38;2;{};{};{}m".format(r, g, b)
def rgb_reset():
	return "\033[38;2;255;255;255m"
def bold():
  return "\033[1m" 
def italics():
  return "\033[3m" 
def underline():
  return "\033[4m" 