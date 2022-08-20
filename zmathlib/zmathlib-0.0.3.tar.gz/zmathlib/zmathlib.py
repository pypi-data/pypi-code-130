def add(a=0,*args):
    result = a
    for z in args:
        result = result + z
    return result

def sub(a=0,*args):
    result = a
    for z in args:
        result = result - z
    return result

def mul(a=0,*args):
    result = a
    for z in args:
        result = result * z
    return result

def div(a=0,*args):
    result = a
    for z in args:
        result = result / z
    return result