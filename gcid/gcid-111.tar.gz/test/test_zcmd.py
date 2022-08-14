# This file is placed in the Public Domain.


"command tests"


import inspect
import random
import unittest


from gcid.object import Object, get
from gcid.handler import Command, Commands


import gcid.basic



events = []
skip = ["cfg",]

param = Object()
param.cmd = [""]
param.cfg = ["nick=gcid", "server=localhost", "port=6699"]
param.fnd = ["log", "log txt==test", "config", "config name=gcid", "config server==localhost"]
param.flt = ["0", ""]
param.log = ["test1", "test2"]
param.mre = [""]
param.thr = [""]


def getmain(name):
    main = __import__("__main__")
    return getattr(main, name, None)


def consume(events):
    fixed = []
    res = []
    for e in events:
        e.wait()
        fixed.append(e)
    for f in fixed:
        try:
            events.remove(f)
        except ValueError:
            continue
    return res


class Test_Commands(unittest.TestCase):

    def test_commands(self):
        c = getmain("c")
        cmds = sorted(Commands.cmd)
        for cmd in cmds:
            if cmd in skip:
                continue
            for ex in get(param, cmd, ""):
                e = Command()
                e.channel = "#gcid"
                e.orig = repr(c)
                txt = cmd + " " + ex
                e.txt = txt.strip()
                c.handle(e)
                events.append(e)
        consume(events)
        self.assertTrue(not events)
