def minmod(r):
    phi=max(0,min(1.0,r))
    return phi

def vanLeer(r):
    absr=abs(r)
    phi=(r+absr)/(1+absr)
    return phi

def Gregori(r):
    phi=max(0,min(2*r,r**0.5,2))
    return phi