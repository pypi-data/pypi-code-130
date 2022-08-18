from yaml import dump

def f(obj, path): dump(obj, open(path,'w'))