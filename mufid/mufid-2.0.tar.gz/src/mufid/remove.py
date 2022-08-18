from mufid.do_nothing import f as do_nothing
from os.path import exists
from os import remove

def f(path): remove(path) if exists(path) else do_nothing()