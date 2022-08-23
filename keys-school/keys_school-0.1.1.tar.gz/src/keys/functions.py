import string
abc=list(string.ascii_lowercase)
from getkey import getkey, keys
from .keynames import all_keys
buffer=[]

def __re_run(Class):
    run(Class, globals()["stop"], globals()["logs"], globals()["wasd"],globals()["coms"])
def __one(key, main, wasd):
    if wasd:
        if key == "w":
            try:
                main.execute(main, "up")
            except Exception as e:
                print(e)
        elif key == "s":
            try:
                main.execute(main, "down")
            except Exception as e:
                print(e)
        elif key == "d":
            try:
                main.execute(main, "right")
            except Exception as e:
                print(e)
        elif key == "a":
            try:
                main.execute(main, "left")
            except Exception as e:
                print(e)
    if key == "up":
        try:
            main.execute(main, "up")
        except Exception as e:
            print(e)
    elif key == "down":
        try:
            main.execute(main, "down")
        except Exception as e:
            print(e)
    elif key == "right":
        try:
            main.execute(main, "right")
        except Exception as e:
            print(e)
    elif key == "left":
        try:
            main.execute(main, "left")
        except Exception as e:
            print(e)
    __re_run(main)

def __two(key, main, wasd):
    if wasd:
        if key == "w":
            try:
                main.execute(main, "up")
            except Exception as e:
                print(e)
        elif key == "s":
            try:
                main.execute(main, "down")
            except Exception as e:
                print(e)
        elif key == "d":
            try:
                main.execute(main, "right")
            except Exception as e:
                print(e)
        elif key == "a":
            try:
                main.execute(main, "left")
            except Exception as e:
                print(e)
    if key == "up":
        try:
            main.execute(main, "up")
        except Exception as e:
            print(e)
    elif key == "down":
        try:
            main.execute(main, "down")
        except Exception as e:
            print(e)
    elif key == "right":
        try:
            main.execute(main, "right")
        except Exception as e:
            print(e)
    elif key == "left":
        try:
            main.execute(main, "left")
        except Exception as e:
            print(e)
    elif key == "space": 
        try:
            main.execute(main, "space")
        except Exception as e:
            print(e)
    __re_run(main)

def __three(key, main, wasd):
    if wasd:
        if key == "w":
            try:
                main.execute(main, "up")
            except Exception as e:
                print(e)
        elif key == "s":
            try:
                main.execute(main, "down")
            except Exception as e:
                print(e)
        elif key == "d":
            try:
                main.execute(main, "right")
            except Exception as e:
                print(e)
        elif key == "a":
            try:
                main.execute(main, "left")
            except Exception as e:
                print(e)
    if key == "up":
        try:
            main.execute(main, "up")
        except Exception as e:
            print(e)
    elif key == "down":
        try:
            main.execute(main, "down")
        except Exception as e:
            print(e)
    elif key == "right":
        try:
            main.execute(main, "right")
        except Exception as e:
            print(e)
    elif key == "left":
        try:
            main.execute(main, "left")
        except Exception as e:
            print(e)
    elif key == "space": 
        try:
            main.execute(main, "space")
        except Exception as e:
            print(e)
    else:
        try:
            if key in abc:
                main.execute(main, key)
        except Exception as e:
            print(e)
    __re_run(main)

def __four(key, main, wasd):
    if wasd:
        if key == "w":
            try:
                main.execute(main, "up")
            except Exception as e:
                print(e)
        elif key == "s":
            try:
                main.execute(main, "down")
            except Exception as e:
                print(e)
        elif key == "d":
            try:
                main.execute(main, "right")
            except Exception as e:
                print(e)
        elif key == "a":
            try:
                main.execute(main, "left")
            except Exception as e:
                print(e)
    if key == "up":
        try:
            main.execute(main, "up")
        except Exception as e:
            print(e)
    elif key == "down":
        try:
            main.execute(main, "down")
        except Exception as e:
            print(e)
    elif key == "right":
        try:
            main.execute(main, "right")
        except Exception as e:
            print(e)
    elif key == "left":
        try:
            main.execute(main, "left")
        except Exception as e:
            print(e)
    elif key == "space": 
        try:
            main.execute(main, "space")
        except Exception as e:
            print(e)
    else:
        try:
            main.execute(main, key)
        except Exception as e:
            print(e)
    __re_run(main)


def run(Class, stop:str="esc", logs:bool=False, wasd=False, coms:int=1):
    key=getkey()
    try:
        all=all_keys[key]
        if all == "something":
            buffer.append(key)
            print(r"REPORT({}): Please give code to either me or the teacher".format(buffer))
            buffer.remove(key)
            return __re_run(Class)
    except:
        pass
    key=keys.name(key).lower()
    if logs:
        print(key)
    globals()["stop"] = stop
    globals()["wasd"] = wasd
    globals()["logs"]=logs
    globals()["Class"]=Class
    if coms <= 4:
        globals()["coms"] = coms
    else:
        return print(f"{coms} is not a number 1-4 (ERROR: 4 doesnt work right now)")
    if key == stop.lower():
        return print("TERMINATED")
    
    elif coms == 1:
        __one(key, Class, wasd)
    elif coms == 2:
        __two(key, Class, wasd)
    elif coms == 3:
        __three(key, Class, wasd)
    elif coms == 4:
        __four(key, Class, wasd)





































































def test(key, x):
    if key == x:
        return True
    return False

class text:
    run = """
keys.run(Class, stop:str="esc", logs:bool=False, wasd=False, coms:int=1):
 **Class(class parameter): the class that the execute function is in
  *stop(key):
    DEFAULT esc
     key: the key that stops the script

  *logs(1, 2, or 3):
    DEFAULT 3 
     1: if you want all buttons logged
     2: if you want some buttons logged
     3: if you want no buttons logged

  *wasd(True or False):
    DEFAULT False
     True: adds wasd to the foward/back/left/right commands
     False: removes wasd from the foward/back/left/right commands
    
  *com(1, 2, 3, 4):
    DEFAULT 1
     1: activates commands for "up" "down" "right" "left"
     2: adds commands for "space" 
     3: adds commands for all normal characters(like abcd, and so on)
     4: adds commands for special characters(like f1, backspace, home, and so on)


EXAMPLES:
  keys.run(Class=Class, keys=1, wasd=False, logs=2) or lib.run(Class, esc, 2, False, 1)"""
    full="""
*OPTIONAL
**REQUIRED

keys.run(Class, logs, wasd):
 **Class(class parameter): the class that the execute function is in
  *stop(key):
    DEFAULT esc
     key: the key that stops the script

  *logs(True or False):
    DEFAULT False 
     True: if you want all buttons logged
     False: if you want no buttons logged

  *wasd(True or False):
    DEFAULT False
     True: adds wasd to the foward/back/left/right commands
     False: removes wasd from the foward/back/left/right commands
    
  *coms(1, 2, 3, 4):
    DEFAULT 1
     1: activates commands for "up" "down" "right" "left"
     2: adds commands for "space" 
     3: adds commands for all normal characters(like abcd, and so on)
     4: adds commands for special characters(like f1, backspace, home, and so on)

EXAMPLES:
  keys.run(Class=Class, com=1, wasd=False, logs=2) or lib.run(Class, esc, 2, False, 1)


If you have further questions/ideas come talk to me or the teacher"""

def help(jj:str="full"):
    if jj.lower() == "run":
        return text.run    
    elif jj=="full": 
        return text.full
    elif jj=="text":
        return 
    else: 
        return f"{jj} is not a command name \n\nPS: do not provide keys.command"