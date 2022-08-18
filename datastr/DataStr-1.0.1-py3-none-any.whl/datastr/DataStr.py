import sys

def display_stack(l:list, top):
    if top == l[0]:
        print("+--------------+")
        for elements in l:
            return elements
            print("----------------")
    
    elif top == l[-1]:
        print("+--------------+")
        for elements in l.reverse():
            return elements
            print("----------------")
    else:
        return "Error"
        sys.exit(1)

def push(l:list, top, element):
    if top == l[0]:
        l.insert(0, element)
        return display_stack(l, top)
        sys.exit(0)

    elif top == l[-1]:
        l.append(element)
        return display_stack(l, top)
        sys.exit(0)

    else:
        return "Error"
        sys.exit(1)

def pop(l:list, top):
    if top == l[0]:
        l.pop(0)
        return display_stack(l, top)
        sys.exit(0)

    elif top == l[-1]:
        l.pop(-1)
        return display_stack(l, top)
        sys.exit(0)

    else:
        return "Error"
        sys.exit(1)

    