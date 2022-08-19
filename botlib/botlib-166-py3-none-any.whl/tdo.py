# This file is placed in the Public Domain.


"todo"


import time


from .obj import Object, find, fntime, save
from .tmr import elapsed


class Todo(Object):

    def __init__(self):
        super().__init__()
        self.txt = ""


def dne(event):
    if not event.args:
        return
    selector = {"txt": event.args[0]}
    for _fn, obj in find("todo", selector):
        obj._deleted = True
        save(obj)
        event.reply("ok")
        break


def tdo(event):
    if not event.rest:
        _nr = 0
        for _fn, obj in find("todo"):
            event.reply("%s %s %s" % (_nr, obj.txt, elapsed(time.time() - fntime(_fn))))
            _nr += 1
        return
    obj = Todo()
    obj.txt = event.rest
    save(obj)
    event.reply("ok")
