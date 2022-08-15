def deletestr(a,b):
    return a.replace(b,'')
def deletegiho(a):
    return (a**2)**0.5
def add(a,b):
    if 'str' in str(type(a)) or 'str' in str(type(b)):
        return str(a)+str(b)
    elif 'float' in str(type(a)) or 'float' in str(type(b)):
        return a+b
    elif 'int' in str(type(a)) or 'int' in str(type(b)):
        return a+b
def lastdigit(a):
    return a[len(a)-1]
def dellastobj(a):
    a.remove(a[len(a)-1])