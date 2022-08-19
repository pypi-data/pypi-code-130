# This file is placed in the Public Domain.


"log"


import time


from .obj import Object, find, fntime, save
from .tmr import elapsed


class Log(Object):

    def __init__(self):
        super().__init__()
        self.txt = ""


def log(event):
    if not event.rest:
        _nr = 0
        for _fn, obj in find("log"):
            event.reply("%s %s %s" % (
                                      _nr,
                                      obj.txt,
                                      elapsed(time.time() - fntime(_fn)))
                                     )
            _nr += 1
        return
    obj = Log()
    obj.txt = event.rest
    save(obj)
    event.reply("ok")
