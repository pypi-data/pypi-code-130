from pynput.keyboard import Key, Listener, KeyCode

__all_keys={'alt': Key.alt,'alt_r': Key.alt_r,'backspace': Key.backspace,'cmd': Key.cmd,
'ctrl': Key.ctrl,'ctrl_r': Key.ctrl_r,'delete': Key.delete,'down': Key.down,'end': Key.end,
'enter': Key.enter,'esc': Key.esc,'f1': Key.f1,'f10': Key.f10,'f11': Key.f11,'f12': Key.f12,
'f13': Key.f13,'f14': Key.f14,'f15': Key.f15,'f16': Key.f16,'f17': Key.f17,'f18': Key.f18,
'f19': Key.f19,'f2': Key.f2,'f20': Key.f20,'f3': Key.f3,'f4': Key.f4,'f5': Key.f5,'f6': Key.f6,
'f7': Key.f7,'f8': Key.f8,'f9': Key.f9,'home': Key.home,'insert': Key.insert,'left': Key.left,
'menu': Key.menu,'pause': Key.pause,'right': Key.right,'shift': Key.shift,'shift_r': Key.shift_r,
'space': Key.space,'tab': Key.tab,'up': Key.up,'page_up': Key.page_up,'page_down': Key.page_down
}
def __all_log(key):
    log=globals()["log"]
    if log == 1 or log == 2:
        try: 
            print(key.char)
        except:
            if log == 1:
                x=str(key).split(".")[1]
                print(x)
def __find_Skey(key:str):
    key = str(key)
    try: 
        globals()["Skey"]=__all_keys[key]
    except Exception as e:
        print(e)
        try:
            globals()["Skey"]=KeyCode.from_char(key)
        except:
            return True
        else:
            return False
    else:
        return False


def __one(key, main, wasd):
    __all_log(key)
    if key == Key.up:
        main.execute(main, "up")
    elif key == Key.down:
        main.execute(main, "down")
    elif key == Key.right:
        main.execute(main, "right")
    elif key == Key.left:
        main.execute(main, "left")
    elif wasd:
        if key == KeyCode.from_char("w"):
            main.execute(main, "up")
        elif key == KeyCode.from_char("s"):
            main.execute(main, "down")
        elif key == KeyCode.from_char("d"):
            main.execute(main, "right")
        elif key == KeyCode.from_char("a"):
            main.execute(main, "left")


def __two(key, main, wasd, log):
    __all_log(key)
    if key == Key.up:
        main.execute(main, "up")
    elif key == Key.down:
        main.execute(main, "down")
    elif key == Key.right:
        main.execute(main, "right")
    elif key == Key.left:
        main.execute(main, "left")
    elif key == Key.space:
        main.execute(main, "space")
    elif wasd:
        if key == KeyCode.from_char("w"):
            main.execute(main, "up")
        elif key == KeyCode.from_char("s"):
            main.execute(main, "down")
        elif key == KeyCode.from_char("d"):
            main.execute(main, "right")
        elif key == KeyCode.from_char("a"):
            main.execute(main, "left")

def __three(key, main, wasd):
    __all_log(key)
    if key == Key.up:
        main.execute(main, "up")
    elif key == Key.down:
        main.execute(main, "down")
    elif key == Key.right:
        main.execute(main, "right")
    elif key == Key.left:
        main.execute(main, "left")
    elif key == Key.space:
        main.execute(main, "space")
    else:
        try:
            current=str(key.char)
        except:
            pass
        else:
            main.execute(main, current)

    if wasd:
        if key == KeyCode.from_char("w"):
            main.execute(main, "up")
        elif key == KeyCode.from_char("s"):
            main.execute(main, "down")
        elif key == KeyCode.from_char("d"):
            main.execute(main, "right")
        elif key == KeyCode.from_char("a"):
            main.execute(main, "left")

def __four(key, main, wasd):
    __all_log(key)
    if key == Key.up:
        main.execute(main, "up")
    elif key == Key.down:
        main.execute(main, "down")
    elif key == Key.right:
        main.execute(main, "right")
    elif key == Key.left:
        main.execute(main, "left")
    elif key == Key.space:
        main.execute(main, "space")
    else:
        try:
            current=str(key.char)
        except:
            current=str(key).split(".")[1].lower()
        finally:
            try:
                main.execute(main, current)
            except Exception as e:
                print(e)

    if wasd:
        if key == KeyCode.from_char("w"):
            main.execute(main, "up")
        elif key == KeyCode.from_char("s"):
            main.execute(main, "down")
        elif key == KeyCode.from_char("d"):
            main.execute(main, "right")
        elif key == KeyCode.from_char("a"):
            main.execute(main, "left")

def __r(key):
    Skey=globals()["Skey"]
    if key == Skey:
        return False   

def __p(key):
    main=globals()["Class"]
    Skey=globals()["Skey"]
    keys=globals()["keys"]
    wasd=globals()["wasd"]
    if key == Skey:
        return False   
    if keys == 1:
        __one(key, main, wasd)
    elif keys == 2:
        __two(key, main, wasd)
    elif keys == 3:
        __three(key, main, wasd)
    elif keys == 4:
        __four(key, main, wasd)     



def run(Class, Skey:str="esc", log:int=3, wasd=False, keys:int=1):
    try:
        Class.execute(Class, "test")
    except:
        return print("make sure you have provided a class object with an execute function nested inside")
    else:
        globals()["Class"]=Class
    if keys <= 4:
        globals()["keys"] = keys
    else:
        return print(f"{keys} is not a number 1-4")
    if log <= 3:
        globals()["log"] = log
    else:
        return print(f"{log} is not a number 1-3")
    if __find_Skey(Skey.lower()):
        return print(f"ERROR: {Skey.lower()} is not a recognized key")
    
    globals()["wasd"] = wasd


    with Listener(on_press=__p, on_release=__r) as l:
        l.start
        l.join()

def test(key, x):
    if key == x:
        return True
    return False












class text:
    run = """
keys.run(Class, log, wasd):
 **Class(class parameter): the class that the execute function is in
  *Skey(key):
    DEFAULT esc
     key: the key that stops the script

  *log(1, 2, or 3):
    DEFAULT 3 
     1: if you want all buttons logged
     2: if you want some buttons logged
     3: if you want no buttons logged

  *wasd(True or False):
    DEFAULT False
     True: adds wasd to the foward/back/left/right commands
     False: removes wasd from the foward/back/left/right commands
    
  *keys(1, 2, 3, 4):
    DEFAULT 1
     1: activates commands for "up" "down" "right" "left"
     2: adds commands for "space" 
     3: adds commands for all normal characters(like abcd, and so on)
     4: adds commands for special characters(like f1, backspace, home, and so on)


EXAMPLES:
  keys.run(Class=Class, keys=1, wasd=False, log=2) or lib.run(Class, esc, 2, False, 1)"""
    full="""
*OPTIONAL
**REQUIRED

keys.run(Class, log, wasd):
 **Class(class parameter): the class that the execute function is in
  *Skey(key):
    DEFAULT esc
     key: the key that stops the script

  *log(1, 2, or 3):
    DEFAULT 3 
     1: if you want all buttons logged
     2: if you want some buttons logged
     3: if you want no buttons logged

  *wasd(True or False):
    DEFAULT False
     True: adds wasd to the foward/back/left/right commands
     False: removes wasd from the foward/back/left/right commands
    
  *keys(1, 2, 3, 4):
    DEFAULT 1
     1: activates commands for "up" "down" "right" "left"
     2: adds commands for "space" 
     3: adds commands for all normal characters(like abcd, and so on)
     4: adds commands for special characters(like f1, backspace, home, and so on)
       IMPORTANT: 4 is still a work in ptogress


EXAMPLES:
  keys.run(Class=Class, keys=1, wasd=False, log=2) or lib.run(Class, esc, 2, False, 1)


If you have further questions/ideas come talk to me or the teacher"""

def help(jj:str="full"):
    if jj.lower() == "run":
        return text.run    
    elif jj=="full": 
        return text.full
    else: 
        return f"{jj} is not a command name \n\nPS: do not provide keys.command"