import random
import os
import time
import colored
from colored import stylize
import curses
import pyfiglet

def transform(string1, string2, tool_type, tool_color):
    replaced = []
    os.system('clear')
    print(stylize("\n {}".format(tool_type),colored.attr("bold")+colored.fg(tool_color)), string1,'\n')
    string1_words = string1.split(' ')
    string2_words = string2.split(' ')

    if len(string1_words) == len(string2_words):
        for i in range(len(string2_words)):
            ra = random.randint(0, len(string2_words)-1)
            while ra in replaced:
                ra = random.randint(0, len(string2_words)-1)
            string1_words[ra] = string2_words[ra]
            time.sleep(0.1)
            os.system('clear')
            print(stylize("\n {}".format(tool_type),colored.attr("bold")+colored.fg(tool_color)), ' '.join(string1_words),'\n')
            replaced.append(ra)

    elif len(string1_words) < len(string2_words):
        string2_words_new = string2_words[0:len(string1_words)]
        remainingList = string2_words[len(string1_words):]
        for i in range(len(string2_words_new)):
            ra = random.randint(0, len(string2_words_new)-1)
            while ra in replaced:
                ra = random.randint(0, len(string2_words_new)-1)
            string1_words[ra] = string2_words_new[ra]
            time.sleep(0.1)
            os.system('clear')
            print(stylize("\n {}".format(tool_type),colored.attr("bold")+colored.fg(tool_color)), ' '.join(string1_words),'\n')
            replaced.append(ra)
        for rem in remainingList:
            string1_words.append(rem)
            time.sleep(0.1)
            os.system('clear')
            print(stylize("\n {}".format(tool_type),colored.attr("bold")+colored.fg(tool_color)), ' '.join(string1_words),'\n')

    else:
        difference = len(string1_words)-len(string2_words)
        for i in range(len(string2_words)):
            ra = random.randint(0, len(string2_words)-1)
            while ra in replaced:
                ra = random.randint(0, len(string2_words)-1)
            string1_words[ra] = string2_words[ra]
            if difference != 0:
                string1_words.pop()
                difference -= 1
            time.sleep(0.1)
            os.system('clear')
            print(stylize("\n {}".format(tool_type),colored.attr("bold")+colored.fg(tool_color)), ' '.join(string1_words),'\n')
            replaced.append(ra)
