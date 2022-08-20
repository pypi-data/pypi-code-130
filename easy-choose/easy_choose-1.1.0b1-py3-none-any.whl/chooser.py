# The chooser.
import random as ra

def chooser(num: int, only: bool=False, *names):
    '''Quickly select num elements from the names.
    Optional - only: Does not repeat the element, 
    but reduces the number of elements returned.'''
    results = []
    for n in range(num):
        result = ra.choice(names)
        results.append(result)
    if only == True:
        return list(set(results))
    return results

def sortchooser(num: int, only: bool=False, *names):
    '''It's the same operation as chooser(), but sorted a bit.'''
    results = []
    for n in range(num):
        result = ra.choice(names)
        results.append(result)
    if only == True:
        return sorted(list(set(results)))
    return sorted(results)

def revchooser(num: int, only: bool=False, *names):
    '''Reverse order.'''
    results = []
    for n in range(num):
        result = ra.choice(names)
        results.append(result)
    if only == True:
        return reversed(list(set(results)))
    return reversed(results)