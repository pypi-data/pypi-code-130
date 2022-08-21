def Lagrange(z, x_values, y_values, n):
    y = 0 
    
    for i in range(n):   
        Lagrangian = 1
    
        for j in range(n):
            if j != i:
                Lagrangian = Lagrangian * (z - x_values[j])/(x_values[i] - x_values[j])
    
        y = y + Lagrangian * y_values[i]
    return y

def twoPtForwardDiff(x, h, x_values, y_values, n):
    forwardDifference = ((Lagrange(x + h, x_values, y_values, n)) - (Lagrange(x, x_values, y_values, n))) / (h)
    return round(forwardDifference, 6)

def twoPtBackwardDiff(x, h, x_values, y_values, n):
    backwardDifference = ((Lagrange(x, x_values, y_values, n)) - (Lagrange(x - h, x_values, y_values, n))) / (h)
    return round(backwardDifference, 6)

def twoPtCentralDiff(x, h, x_values, y_values, n):
    centralDifference = ((Lagrange(x + h, x_values, y_values, n)) - (Lagrange(x - h, x_values, y_values, n))) / (2 * h)
    return round(centralDifference, 6)

def threePtBackwardDiff(x, h, x_values, y_values, n):
    threePointBackwardDifference = (1 / (2 * h)) * ((Lagrange(x - (2 * h), x_values, y_values, n)) - (4 * Lagrange(x - h, x_values, y_values, n)) + (3 * Lagrange(x, x_values, y_values, n)))
    return round(threePointBackwardDifference, 6)
    
    
def threePtForwardDiff(x, h, x_values, y_values, n):
    threePointForwardDifference = (1 / (2 * h)) * ((-3 * Lagrange(x, x_values, y_values, n)) + (4 * Lagrange(x + h, x_values, y_values, n)) - (Lagrange(x + (2 * h), x_values, y_values, n)))
    return round(threePointForwardDifference, 6)


def threePtCentralDiff(x, h, x_values, y_values, n):
    threePointCenterDifference = (Lagrange(x + h, x_values, y_values, n) - Lagrange(x - h, x_values, y_values, n)) / (2 * h)
    return round(threePointCenterDifference, 6)

def bisectionMethod(f, x1, x2, err):

    moreNums, lessNums = {}, {}
    
    for i in range (x1, x2 + 1):
        if f(i) >= 0:
            moreNums[i] = f(i)
        else:
            lessNums[i] = f(i)
    
    lower = max(lessNums)
    higher = min(moreNums)
    x0 = (lower + higher) / 2
    iterations = 0
    
    while f(x0) < -err or f(x0) > err:
        
        x0 = (lower + higher) / 2
        if f(x0) > 0:
            higher = x0
        else:
            lower = x0
        iterations += 1
        
    return round(x0, 6), iterations

def regulaFalsiMethod(f, x1, x2, err):

    moreNums, lessNums = {}, {}
    
    for i in range (x1, x2 + 1):
        if f(i) >= 0:
            moreNums[i] = f(i)
        else:
            lessNums[i] = f(i)
            
    lower = max(lessNums)
    higher = min(moreNums)
    x0 = (lower * f(higher) - higher * f(lower)) / (f(higher) - f(lower))
    iterations = 0
    
    while f(x0) < -err or f(x0) > err:
        
        x0 = (lower * f(higher) - higher * f(lower)) / (f(higher) - f(lower))
        
        if f(x0) > 0:
            higher = x0
        else:
            lower = x0
        iterations += 1
        
    return round(x0, 6), iterations
    
def newtonRaphsonMethod(f, derivative, x1, x2, err):
    
    moreNums, lessNums = {}, {}
    
    for i in range (x1, x2 + 1):
        if f(i) >= 0:
            moreNums[i] = f(i)
        else:
            lessNums[i] = f(i)
            
    lower = max(lessNums)
    higher = min(moreNums)
    x0 = (lower + higher) / 2
    iterations = 1
    
    while f(x0) < -err or f(x0) > err:
        
        x0 = x0 - (f(x0) / derivative(x0))
        
        iterations += 1
    return round(x0, 6), iterations

def secantMethod(f, x1, x2, err):
    
    moreNums, lessNums = {}, {}
    
    for i in range (x1, x2 + 1):
        if f(i) >= 0:
            moreNums[i] = f(i)
        else:
            lessNums[i] = f(i)
            
    lower = max(lessNums)
    higher = min(moreNums)
    x0 = (lower * f(higher) - higher * f(lower)) / (f(higher) - f(lower))
    iterations = 0
    
    while f(x0) < -err or f(x0) > err:
        
        x0 = (lower * f(higher) - higher * f(lower)) / (f(higher) - f(lower))
        
        if iterations % 2 != 0:
            higher = x0
        else:
            lower = x0
        iterations += 1

    return round(x0, 6), iterations

def lagrangeInterpolation(x, x_values, y_values):
    res = []
    for n in range(len(x_values)):
        top, bottom = 1, 1
        for i in range(1, len(x_values)):
            top = top * (x - x_values[n - i])
            bottom = bottom * (x_values[n] - x_values[n - i])

        res.append((top / bottom) * y_values[n])
        
    return round(sum(res), 6)

def lagrangeReverseInterpolation(y, x_values, y_values):
    res = []
    for n in range(len(y_values)):
        top, bottom = 1, 1
        for i in range(1, len(y_values)):
            top = top * (y - y_values[n - i])
            bottom = bottom * (y_values[n] - y_values[n - i])

        res.append((top / bottom) * x_values[n])
        
    return round(sum(res), 6)

def trapezoidalRule(x_values, y_values):
    h = x_values[1] - x_values[0]
    return round((h / 2) * (y_values[0] + y_values[len(y_values)-1] + 2*(sum(y_values[1:len(y_values)-1]))), 6)

def simpsonsOneThirdRule(x_values, y_values):
    
    h = x_values[1] - x_values[0]
    odds, evens = [], []
    
    for i in range(1, len(y_values)-1):
        if i % 2 == 0:
            evens.append(y_values[i])
        else:
            odds.append(y_values[i])
            
    return round((h / 3) * ((y_values[0] + y_values[len(y_values)-1]) + 4*(sum(odds)) + 2 * sum(evens)), 6)

def simpsonsThreeEigthRule(x_values, y_values):
    
    h = x_values[1] - x_values[0]
    odds, evens = [], []
    
    for i in range(1, len(y_values)-1):
        if i % 3 != 0:
            evens.append(y_values[i])
        else:
            odds.append(y_values[i])
            
    return round(((3 * h) / 8) * ((y_values[0] + y_values[len(y_values)-1]) + 2*(sum(odds)) + 3 * sum(evens)), 6)