def deletestr(a,b):
    return a.replace(b,'')
    
def deletesymbol(a):
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
    
def average(a):
    b=0
    for i in range(len(a)):
        b+=a[i]
    b=b/(len(a))
    return b
    
def mode(a):
    d=[]
    b=[]
    b.append(a[0])
    for i in range (len(a)):
        c=0
        for j in range (len(b)):
            if a[i]==b[j]:pass
            else:
                c=c+1
        if c==len(b):
            b.append(a[i])
    for i in range (len(b)):
        d.append('')
    for i in range (len(b)):
        hm=0
        for j in range (len(a)):
            if b[i]==a[j]:
                hm=hm+1
        d[i]=hm
    hmm=max(d)
    largest=[]
    h=0
    for i in range (len(d)):
        if d[i]==d[0]:
            h=h+1
    if h==len(d):
        return 'There is no mode.'
    else:
        for i in range (len(d)):
            if max(d)==d[i]:
                largest.append(b[i])
        return largest
        
def median(a):
    d=[]
    for i in range (len(a)):
        d.append(a[i])
    d.sort()
    if len(d)%2==0:
        b=(d[int((len(d))/2)]+d[int((len(d))/2-1)])/2
    elif len(d)%2==1:
        b=d[int((len(d)-1)/2)]
    return b
def deviation(a):
    b=0
    for i in range (len(a)):
        b+=a[i]
    b=b/(len(a))
    c=[]
    for i in range (len(a)):
        c.append(a[i]-b)
    return c
def variance(a):
    b=0
    for i in range (len(a)):
        b+=a[i]
    b=b/(len(a))
    c=[]
    for i in range (len(a)):
        c.append(a[i]-b)
    d=0
    for i in range (len(a)):
        d=d+((c[i])**2)
    d=d/5
    return d
def standevia(a):
    b=0
    for i in range (len(a)):
        b+=a[i]
    b=b/(len(a))
    c=[]
    for i in range (len(a)):
        c.append(a[i]-b)
    d=0
    for i in range (len(a)):
        d=d+((c[i])**2)
    d=d/5
    d=d**(1/2)
    return d