# The chooser.

# Import random.py
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
        if num == 1:
            return str(list(set(results)))
        return list(set(results))
    if num == 1:
        return str(results)
    return results

def sortchooser(num: int, only: bool=False, *names):
    '''It's the same operation as chooser(), but sorted a bit.'''
    results = []
    for n in range(num):
        result = ra.choice(names)
        results.append(result)
    if only == True:
        if num == 1:
            return str(sorted(list(set(results))))
        return sorted(list(set(results)))
    if num == 1:
        return str(sorted(results))
    return sorted(results)

def revchooser(num: int, only: bool=False, *names):
    '''Reverse order.'''
    results = []
    for n in range(num):
        result = ra.choice(names)
        results.append(result)
    if only == True:
        if num == 1:
            return str(reversed(list(set(results))))
        return reversed(list(set(results)))
    if num == 1:
        return str(reversed(results))
    return reversed(results)