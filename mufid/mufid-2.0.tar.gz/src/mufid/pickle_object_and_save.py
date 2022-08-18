from pickle import dump

def f(some_object, path): dump(some_object, open(path, 'ab'))
