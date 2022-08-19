# This file is placed in the Public Domain.
# pylint: disable=E1101,E0611,C0116,C0413


"list of objects"


from rssbot.obj import Object


class Bus(Object):

    objs = []

    @staticmethod
    def add(obj):
        if repr(obj) not in [repr(x) for x in Bus.objs]:
            Bus.objs.append(obj)

    @staticmethod
    def announce(txt):
        for obj in Bus.objs:
            if obj and "announce" in dir(obj):
                obj.announce(txt)

    @staticmethod
    def byorig(orig):
        res = None
        for obj in Bus.objs:
            if repr(obj) == orig:
                res = obj
                break
        return res

    @staticmethod
    def say(orig, channel, txt):
        obj = Bus.byorig(orig)
        if obj and "say" in dir(obj):
            obj.say(channel, txt)
