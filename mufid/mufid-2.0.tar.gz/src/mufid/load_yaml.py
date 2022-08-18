from yaml import load
from yaml import FullLoader

def f(path): return load(open(path, 'r').read(), Loader=FullLoader)