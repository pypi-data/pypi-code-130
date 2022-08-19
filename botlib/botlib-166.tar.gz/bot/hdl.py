# pylint: disable=E1101,E0611,C0116,C0413
# This file is placed in the Public Domain.


"handler"


import queue
import threading
import time
import op


from .bus import Bus
from .obj import Default, Object, get, launch, register, update


def __dir__():
    return (
        'Callbacks',
        'Cfg',
        'Client',
        "Command",
        "Event",
        'Handler',
        "Parsed"
        'dispatch',
        "docmd",
        "parse",
        'starttime',
        'wait'
    )


starttime = time.time()


Cfg = Default()
Cfg.debug = False
Cfg.name = ""
Cfg.verbose = False


class Callbacks(Object):

    cbs = Object()

    @staticmethod
    def add(name, cbs):
        register(Callbacks.cbs, name, cbs)

    @staticmethod
    def callback(event):
        func = Callbacks.get(event.type)
        if not func:
            event.ready()
            return
        func(event)

    @staticmethod
    def get(cmd):
        return get(Callbacks.cbs, cmd)

    @staticmethod
    def dispatch(event):
        Callbacks.callback(event)


class Commands(Object):

    cmd = Object()

    @staticmethod
    def add(cmd):
        register(Commands.cmd, cmd.__name__, cmd)

    @staticmethod
    def get(cmd):
        return get(Commands.cmd, cmd)


    @staticmethod
    def remove(cmd):
        del Commands.cmd[cmd]


class Handler(Object):

    def __init__(self):
        Object.__init__(self)
        self.cache = Object()
        self.queue = queue.Queue()
        self.stopped = threading.Event()
        self.threaded = False
        Bus.add(self)

    def announce(self, txt):
        self.raw(txt)

    @staticmethod
    def forever():
        while 1:
            time.sleep(1.0)

    @staticmethod
    def handle(event):
        Callbacks.dispatch(event)

    def loop(self):
        while not self.stopped.isSet():
            self.handle(self.poll())

    def poll(self):
        return self.queue.get()

    def put(self, event):
        self.queue.put_nowait(event)

    def raw(self, txt):
        pass

    @staticmethod
    def register(typ, cbs):
        Callbacks.add(typ, cbs)

    def restart(self):
        self.stop()
        self.start()

    def say(self, channel, txt):
        self.raw(txt)

    def start(self):
        self.stopped.clear()
        launch(self.loop)

    def stop(self):
        self.stopped.set()


class Client(Handler):

    def __init__(self, orig=None):
        Handler.__init__(self)
        self.gotcha = False
        self.orig = repr(self)

    def announce(self, txt):
        self.raw(txt)

    def raw(self, txt):
        self.gotcha = True

    def say(self, channel, txt):
        self.raw(txt)


class Parsed(Object):

    def __init__(self):
        Object.__init__(self)
        self.args = []
        self.cmd = ""
        self.gets = Default()
        self.index = 0
        self.opts = ""
        self.rest = ""
        self.sets = Default()
        self.toskip = Default()
        self.otxt = ""
        self.txt = ""

    def parse(self, txt=None):
        self.otxt = txt or self.txt
        spl = self.otxt.split()
        args = []
        _nr = -1
        for word in spl:
            if word.startswith("-"):
                try:
                    self.index = int(word[1:])
                except ValueError:
                    self.opts += word[1:2]
                continue
            try:
                key, value = word.split("==")
                if value.endswith("-"):
                    value = value[:-1]
                    self.toskip[value] = ""
                self.gets[key] = value
                continue
            except ValueError:
                pass
            try:
                key, value = word.split("=")
                self.sets[key] = value
                continue
            except ValueError:
                pass
            _nr += 1
            if _nr == 0:
                self.cmd = word
                continue
            args.append(word)
        if args:
            self.args = args
            self.rest = " ".join(args)
            self.txt = self.cmd + " " + self.rest
        else:
            self.txt = self.cmd


class Event(Parsed):

    def __init__(self):
        Parsed.__init__(self)
        self._exc = None
        self._ready = threading.Event()
        self._result = []
        self._thrs = []
        self.cmd = ""
        self.channel = ""
        self.orig = None
        self.type = "event"

    def bot(self):
        return Bus.byorig(self.orig)

    def handle(self):
        pass

    def ready(self):
        self._ready.set()

    def reply(self, txt):
        self._result.append(txt)

    def show(self):
        assert self.orig
        for txt in self._result:
            Bus.say(self.orig, self.channel, txt)

    def wait(self):
        self._ready.wait()
        for thr in self._thrs:
            thr.join()
        return self._result


class Command(Event):

    def __init__(self):
        Event.__init__(self)
        self.type = "command"


def cb_dispatch(event):
    event.parse()
    func = Commands.get(event.cmd)
    if func:
        func(event)
        event.show()
    event.ready()


def cb_handle(event):
    event.parse()
    event.handle()
    event.show()
    event.ready()


Callbacks.add("command", cb_dispatch)
#Callbacks.add("event", cb_handle)


def docmd(clt, txt):
    cmd = Command()
    cmd.channel = ""
    cmd.orig = repr(clt)
    cmd.txt = txt
    clt.handle(cmd)
    cmd.wait()
    return cmd


def parse(txt):
    prs = Parsed()
    prs.parse(txt)
    update(Cfg, prs)
    if "v" in Cfg.opts:
        Cfg.verbose = True


def wait():
    while 1:
        time.sleep(1.0)
