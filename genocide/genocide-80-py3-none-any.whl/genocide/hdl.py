# This file is placed in the Public Domain.


"handler"


import inspect
import queue
import threading
import time
import types


from .obj import Class, Default, Object, get, register, update


def __dir__():
    return (
        'Bus',
        'Callbacks',
        'Cfg',
        'Client',
        "Command",
        "Event",
        'Handler',
        "Parsed"
        "Thread",
        "docmd",
        "getname",
        "launch",
        "parse",
        "scan"
    )


starttime = time.time()


Cfg = Default()
Cfg.console = False
Cfg.debug = False
Cfg.name = ""
Cfg.verbose = False


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


class Thread(threading.Thread):

    def __init__(self, func, name, *args, daemon=True):
        super().__init__(None, self.run, name, (), {}, daemon=daemon)
        self._exc = None
        self._evt = None
        self.name = name
        self.queue = queue.Queue()
        self.queue.put_nowait((func, args))
        self._result = None

    def __iter__(self):
        return self

    def __next__(self):
        for k in dir(self):
            yield k

    def join(self, timeout=None):
        super().join(timeout)
        return self._result

    def run(self):
        func, args = self.queue.get()
        if args:
            self._evt = args[0]
        self.setName(self.name)
        self._result = func(*args)
        return self._result


def dispatch(event):
    event.parse()
    func = Commands.get(event.cmd)
    if func:
        func(event)
        event.show()
    event.ready()


Callbacks.add("command", dispatch)


def docmd(clt, txt):
    cmd = Command()
    cmd.channel = ""
    cmd.orig = repr(clt)
    cmd.txt = txt
    clt.handle(cmd)
    cmd.wait()
    return cmd


def getname(obj):
    typ = type(obj)
    if isinstance(typ, types.ModuleType):
        return obj.__name__
    if "__self__" in dir(obj):
        return "%s.%s" % (obj.__self__.__class__.__name__, obj.__name__)
    if "__class__" in dir(obj) and "__name__" in dir(obj):
        return "%s.%s" % (obj.__class__.__name__, obj.__name__)
    if "__class__" in dir(obj):
        return obj.__class__.__name__
    if "__name__" in dir(obj):
        return obj.__name__
    return None


def launch(func, *args, **kwargs):
    name = kwargs.get("name", getname(func))
    thr = Thread(func, name, *args)
    thr.start()
    return thr


def parse(txt):
    prs = Parsed()
    prs.parse(txt)
    update(Cfg, prs)
    if "v" in Cfg.opts:
        Cfg.verbose = True
    if "c" in Cfg.opts:
        Cfg.console = True

def scan(mod, add=True):
    for _k, obj in inspect.getmembers(mod, inspect.isfunction):
        if "event" in obj.__code__.co_varnames:
            if add:
                Commands.add(obj)
    for _k, clz in inspect.getmembers(mod, inspect.isclass):
        Class.add(clz)
