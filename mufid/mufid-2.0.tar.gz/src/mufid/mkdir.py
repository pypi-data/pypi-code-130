from genericpath import exists
from mufid.do_nothing import f as do_nothing
from os.path import exists
from os import mkdir

def f(path) : return [mkdir(path) if not exists(path) else do_nothing(), path][1]
