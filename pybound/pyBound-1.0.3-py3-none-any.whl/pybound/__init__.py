__version__ = '1.0.3'

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
      if string.startswith("\033") == False and string.startswith("\x1b") == False:
        file.flush()
        sleep(time)
    num -= 1
    if num != 0 and str(strings[len(strings)-num-1]).startswith("\033") == False and str(strings[len(strings)-num-1]).startswith("\x1b") == False:
      file.write(sep)
      file.flush()	
  file.flush()
  file.write(end)
  file.flush()
  
def wait(time = 1):
	sleep(time)
  
def rgb_fore(r, g, b):
		return f'\033[38;2;{r};{g};{b}m'
	
def rgb_back(r, g, b):
    return f'\033[48;2;{r};{g};{b}m'
  
def end():
  return "\033[0m"	
  
def bold():
  return "\033[1m" 
  
def faint():
  return "\033[2m"
  
def italic():
  return "\033[3m" 
  
def underline():
  return "\033[4m" 
  
def blink_slow():
	return "\033[5m"
  
def blink_fast():
	return "\033[6m"
  
def negative():
	return "\033[7m"
  
def conceal():
  return "\033[8m"
  
def crossed():
	return "\033[9m"