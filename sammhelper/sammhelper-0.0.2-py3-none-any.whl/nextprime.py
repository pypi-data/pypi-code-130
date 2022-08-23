import numpy as np

def nextprime(n):
    p=n+1
    for i in range(2,p):
        if(np.mod(p,i)==0):
            p=p+1
        else:
            return p