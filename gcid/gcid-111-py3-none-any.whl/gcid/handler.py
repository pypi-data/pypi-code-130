# This file is placed in the Public Domain.


"event handler"


import queue
import threading
import time
import types


import gcid.object as obj


from .object import Class, Config, Default, Object, get, items, register, spl


def __dir__():
    return (
        'Bus',
        'CLI',
        'Callbacks',
        'Class',
        'Command',
        'Commands',
        'Config',
        'Console',
        'Event',
        'Handler',
        'Table',
        'Thread',
        'boot',
        'dispatch',
        'getname',
        'init',
        'launch',
        'starttime',
    )


starttime = time.time()



class Event(Object):

    def __init__(self):
        super().__init__()
        self._exc = None
        self._ready = threading.Event()
        self._result = []
        self._thrs = []
        self.args = []
        self.channel = ""
        self.cmd = ""
        self.gets = Default()
        self.index = 0
        self.opts = ""
        self.orig = ""
        self.rest = ""
        self.sets = Default()
        self.otxt = ""
        self.txt = ""
        self.type = "event"

    def bot(self):
        return Bus.byorig(self.orig)

    def parse(self, txt=None, orig=None):
        self.otxt = txt or self.txt
        self.orig = orig or self.orig
        splitted = self.otxt.split()
        args = []
        _nr = -1
        for w in splitted:
            _nr += 1
            if w.startswith("-"):
                try:
                    self.index = int(w[1:])
                except ValueError:
                    self.opts += w[1:2]
                continue
            if _nr == 0:
                self.cmd = w
                continue
            try:
                k, v = w.split("==")
                self.gets[k] = v
                continue
            except ValueError:
                pass
            try:
                k, v = w.split("=")
                self.sets[k] = v
                continue
            except ValueError:
                args.append(w)
        if args:
            self.args = args
            self.rest = " ".join(args)
            self.txt = self.cmd + " " + self.rest
        else:
            self.txt = self.cmd

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


class Bus(Object):

    objs = []

    @staticmethod
    def add(o):
        if repr(o) not in [repr(x) for x in Bus.objs]:
            Bus.objs.append(o)

    @staticmethod
    def announce(txt):
        for o in Bus.objs:
            o.announce(txt)

    @staticmethod
    def byorig(orig):
        for o in Bus.objs:
            if repr(o) == orig:
                return o

    @staticmethod
    def say(orig, channel, txt):
        o = Bus.byorig(orig)
        if o:
            o.say(channel, txt)


class Callbacks(Object):

    cbs = Object()
    errors = []
    threaded = True

    @staticmethod
    def add(name, cb):
        register(Callbacks.cbs, name, cb)

    @staticmethod
    def callback(e):
        f = Callbacks.get(e.type)
        if not f:
            e.ready()
            return
        try:
            f(e)
        except Exception as ex:
            Callbacks.errors.append(ex)
            e.ready()

    @staticmethod
    def get(cmd):
        return get(Callbacks.cbs, cmd)

    @staticmethod
    def dispatch(e):
        if Callbacks.threaded:
            e._thrs.append(launch(Callbacks.callback, e, name=e.txt))
            return
        Callbacks.callback(e)



class Commands(Object):

    cmd = Object()

    @staticmethod
    def add(command):
        register(Commands.cmd, command.__name__, command)

    @staticmethod
    def get(command):
        f =  get(Commands.cmd, command)
        return f


    @staticmethod
    def remove(command):
        del Commands.cmd[command]


class Handler(Object):

    def __init__(self):
        Object.__init__(self)
        self.cache = Object()
        self.cfg = Config()
        self.queue = queue.Queue()
        self.stopped = threading.Event()
        self.threaded = False
        Bus.add(self)

    def announce(self, txt):
        self.raw(txt)

    def forever(self):
        while 1:
            time.sleep(1.0)

    def handle(self, e):
        Callbacks.dispatch(e)

    def loop(self):
        while not self.stopped.isSet():
            self.handle(self.poll())

    def poll(self):
        return self.queue.get()

    def put(self, e):
        self.queue.put_nowait(e)

    def raw(self, txt):
        pass

    def register(self, typ, cb):
        Callbacks.add(typ, cb)

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


class CLI(Handler):

    def announce(self, txt):
        self.raw(txt)

    def cmd(self, txt):
        c = Command()
        c.channel = ""
        c.orig = repr(self)
        c.txt = txt
        self.handle(c)
        c.wait()

    def raw(self, txt):
        pass


class Console(CLI):

    def handle(self, e):
        Handler.handle(self, e)
        e.wait()

    def poll(self):
        e = Command()
        e.channel = ""
        e.cmd = ""
        e.txt = input("> ")
        e.orig = repr(self)
        if e.txt:
            e.cmd = e.txt.split()[0]
        return e

    def forever(self):
        while 1:
            time.sleep(1.0)


class Table():

    mod = {}

    @staticmethod
    def add(o):
        Table.mod[o.__name__] = o

    @staticmethod
    def get(nm):
        return Table.mod.get(nm, None)


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
        ""
        super().join(timeout)
        return self._result

    def run(self):
        ""
        func, args = self.queue.get()
        if args:
            self._evt = args[0]
        self.setName(self.name)
        self._result = func(*args)
        return self._result


def boot(txt):
    e = Event()
    e.parse(txt)
    for k, v in items(e):
        setattr(obj.Config, k, v)
    for o in obj.Config.opts:
        if o == "c":
            obj.Config.console = True
        if o == "v":
            obj.Config.verbose = True
    return obj.Config


def dispatch(e):
    e.parse()
    f = Commands.get(e.cmd)
    if f:
        f(e)
        e.show()
    e.ready()


def getname(o):
    t = type(o)
    if isinstance(t, types.ModuleType):
        return o.__name__
    if "__self__" in dir(o):
        return "%s.%s" % (o.__self__.__class__.__name__, o.__name__)
    if "__class__" in dir(o) and "__name__" in dir(o):
        return "%s.%s" % (o.__class__.__name__, o.__name__)
    if "__class__" in dir(o):
        return o.__class__.__name__
    if "__name__" in dir(o):
        return o.__name__
    return None


def init(mns, pn=None, cmds="init"):
    for mn in spl(mns):
        if pn:
            mn = pn + "." + mn
        mod = Table.get(mn)
        if not mod:
            continue
        for cmd in spl(cmds):
            c = getattr(mod, cmd, None)
            if not c:
                continue
            c()


def launch(func, *args, **kwargs):
    name = kwargs.get("name", getname(func))
    t = Thread(func, name, *args)
    t.start()
    return t


Callbacks.add("command", dispatch)
