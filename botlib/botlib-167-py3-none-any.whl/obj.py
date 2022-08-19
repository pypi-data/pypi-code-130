# This file is placed in the Public Domain.
# pylint: disable=E1101,E0611,C0116,C0413


"object"


import copy as copying
import datetime
import inspect
import json
import os
import pathlib
import queue
import threading
import time
import types
import uuid
import _thread


dblock = _thread.allocate_lock()



def __dir__():
    return (
        "Class",
        "Db",
        'NOPATH',
        'Object',
        'ObjectDecoder',
        'ObjectEncoder',
        'Wd',
        'all',
        'clear',
        'copy',
        'diff',
        'dump',
        'dumps',
        'edit',
        "find",
        "fntime",
        "last"
        'fromkeys',
        'get',
        'getname',
        'items',
        'keys',
        'last',
        'launch',
        'load',
        'loads',
        'matchkey',
        'pop',
        'popitem',
        'prt',
        'read',
        "register",
        'save',
        'search',
        'setdefault',
        'update',
        'values',
    )


class NOPATH(Exception):

    pass



class Object:

    "object"

    __slots__ = (
        "__dict__",
        "__otype__",
        "__stp__",
    )


    def __init__(self):
        object.__init__(self)
        self.__otype__ = str(type(self)).split()[-1][1:-2]
        self.__stp__ = os.path.join(
            self.__otype__,
            str(uuid.uuid4()),
            os.sep.join(str(datetime.datetime.now()).split()),
        )

    def __class_getitem__(cls):
        return cls.__dict__.__class_getitem__(cls)

    def __contains__(self, key):
        if key in self.__dict__.keys():
            return True
        return False

    def __delitem__(self, key):
        if key in self:
            del self.__dict__[key]

    def __eq__(self, oobj):
        return len(self.__dict__) == len(oobj.__dict__)

    def __getitem__(self, key):
        return self.__dict__[key]

    def __ior__(self, oobj):
        return self.__dict__.__ior__(oobj)

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    def __le__(self, oobj):
        return len(self) <= len(oobj)

    def __lt__(self, oobj):
        return len(self) < len(oobj)

    def __ge__(self, oobj):
        return len(self) >= len(oobj)

    def __gt__(self, oobj):
        return len(self) > len(oobj)

    def __hash__(self):
        return id(self)

    def __ne__(self, oobj):
        return len(self.__dict__) != len(oobj.__dict__)

    def __reduce__(self):
        pass

    def __reduce_ex__(self, key):
        pass

    def __reversed__(self):
        return self.__dict__.__reversed__()

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __oqn__(self):
        return "<%s.%s object at %s>" % (
            self.__class__.__module__,
            self.__class__.__name__,
            hex(id(self)),
        )

    def __ror__(self, oobj):
        return self.__dict__.__ror__(oobj)

    def __str__(self):
        return str(self.__dict__)


class ObjectDecoder(json.JSONDecoder):

    def decode(self, s, _w=None):
        value = json.loads(s)
        oobj = Object()
        update(oobj, value)
        return oobj


class ObjectEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, dict):
            return o.items()
        if isinstance(o, Object):
            return vars(o)
        if isinstance(o, list):
            return iter(o)
        if isinstance(o,
                      (type(str), type(True), type(False),
                       type(int), type(float))):
            return o
        try:
            return json.JSONEncoder.default(self, o)
        except TypeError:
            return str(o)


class Default(Object):

    def __getattr__(self, key):
        return self.__dict__.get(key, "")


class Wd(Object):

    workdir = ""


def clear(oobj):
    oobj.__dict__ = {}


def copy(oobj):
    return copying.copy(oobj)


def diff(obj1, obj2):
    res = Object()
    keyz = keys(obj1)
    for key in keys(obj2):
        if key in keyz and obj1[key] != obj2[key]:
            res[key] = obj2[key]
    return res


def dump(oobj, opath):
    if opath.split(os.sep)[-1].count(":") == 2:
        dirpath = os.path.dirname(opath)
    pathlib.Path(dirpath).mkdir(parents=True, exist_ok=True)
    with open(opath, "w", encoding="utf-8") as ofile:
        json.dump(
            oobj.__dict__, ofile, cls=ObjectEncoder, indent=4, sort_keys=True
        )
    return oobj.__stp__


def dumps(oobj):
    return json.dumps(oobj, cls=ObjectEncoder)


def edit(oobj, setter):
    for key, value in items(setter):
        register(oobj, key, value)


def prt(oobj, args="", skip="_", empty=False, plain=False, **kwargs):
    keyz = list(keys(oobj))
    res = []
    if args:
        try:
            keyz = args.split(",")
        except (TypeError, ValueError):
            pass
    for key in keyz:
        try:
            skips = skip.split(",")
            if key in skips or key.startswith("_"):
                continue
        except (TypeError, ValueError):
            pass
        value = getattr(oobj, key, None)
        if isinstance(value, Default):
            continue
        if not value and not empty:
            continue
        if " object at " in str(value):
            continue
        txt = ""
        if plain:
            txt = str(value)
        elif isinstance(value, str) and len(value.split()) >= 2:
            txt = '%s="%s"' % (key, value)
        else:
            txt = '%s=%s' % (key, value)
        res.append(txt)
    return " ".join(res)


def fromkeys(iterable, value=None):
    oobj = Object()
    for i in iterable:
        oobj[i] = value
    return oobj


def get(oobj, key, default=None):
    return oobj.__dict__.get(key, default)


def items(oobj):
    try:
        return oobj.__dict__.items()
    except AttributeError:
        return oobj.items()


def matchkey(oobj, key, default=None):
    res = None
    for key2 in keys(oobj):
        if key.lower() in key2.lower():
            res = key2
            break
    return res


def keys(oobj):
    try:
        return oobj.__dict__.keys()
    except (AttributeError, TypeError):
        return oobj.keys()


def load(oobj, opath):
    if opath.count(os.sep) != 3:
        raise NOPATH(opath)
    assert Wd.workdir
    splitted = opath.split(os.sep)
    stp = os.sep.join(splitted[-4:])
    lpath = os.path.join(Wd.workdir, "store", stp)
    if os.path.exists(lpath):
        with open(lpath, "r", encoding="utf-8") as ofile:
            res = json.load(ofile, cls=ObjectDecoder)
            update(oobj, res)
    oobj.__stp__ = stp
    return oobj.__stp__


def loads(name):
    return json.loads(name, cls=ObjectDecoder)


def pop(oobj, key, default=None):
    try:
        return oobj[key]
    except KeyError as ex:
        if default:
            return default
        raise KeyError from ex


def popitem(oobj):
    key = keys(oobj)
    if key:
        value = oobj[key]
        del oobj[key]
        return (key, value)
    raise KeyError


def register(oobj, key, value):
    setattr(oobj, key, value)


def save(oobj, stime=None):
    assert Wd.workdir
    prv = os.sep.join(oobj.__stp__.split(os.sep)[:2])
    oobj.__stp__ = os.path.join(prv,
                             os.sep.join(str(datetime.datetime.now()).split()))
    opath = os.path.join(Wd.workdir, "store", oobj.__stp__)
    dump(oobj, opath)
    os.chmod(opath, 0o444)
    return oobj.__stp__


def search(oobj, selector):
    res = False
    for key, value in items(selector):
        val = get(oobj, key)
        if value in str(val):
            res = True
            break
    return res


def setdefault(oobj, key, default=None):
    if key not in oobj:
        oobj[key] = default
    return oobj[key]


def update(oobj, data):
    try:
        oobj.__dict__.update(vars(data))
    except TypeError:
        oobj.__dict__.update(data)
    return oobj


def values(oobj):
    try:
        return oobj.__dict__.values()
    except TypeError:
        return oobj.values()


class Class():

    cls = {}

    @staticmethod
    def add(clz):
        Class.cls["%s.%s" % (clz.__module__, clz.__name__)] =  clz

    @staticmethod
    def full(name):
        name = name.lower()
        res = []
        for cln in Class.cls:
            if cln.split(".")[-1].lower() == name:
                res.append(cln)
        return res

    @staticmethod
    def get(name):
        return Class.cls.get(name, None)

    @staticmethod
    def remove(name):
        del Class.cls[name]


class Db(Object):

    names = Object()

    @staticmethod
    def all(otype, timed=None):
        result = []
        for fnm in fns(otype, timed):
            oobj = hook(fnm)
            if "_deleted" in oobj and oobj._deleted:
                continue
            result.append((fnm, oobj))
        if not result:
            return []
        return result

    @staticmethod
    def find(otype, selector=None, index=None, timed=None):
        if selector is None:
            selector = {}
        _nr = -1
        result = []
        for fnm in fns(otype, timed):
            oobj = hook(fnm)
            if selector and not search(oobj, selector):
                continue
            if "_deleted" in oobj and oobj._deleted:
                continue
            _nr += 1
            if index is not None and _nr != index:
                continue
            result.append((fnm, oobj))
        return result

    @staticmethod
    def lastmatch(otype, selector=None, index=None, timed=None):
        dbs = Db()
        res = sorted(dbs.find(otype, selector, index, timed),
                     key=lambda x: fntime(x[0]))
        if res:
            return res[-1]
        return (None, None)

    @staticmethod
    def lasttype(otype):
        fnn = fns(otype)
        if fnn:
            return hook(fnn[-1])
        return None

    @staticmethod
    def lastfn(otype):
        fnm = fns(otype)
        if fnm:
            fnn = fnm[-1]
            return (fnn, hook(fnn))
        return (None, None)

    @staticmethod
    def remove(otype, selector=None):
        has = []
        for _fn, oobj in Db.find(otype, selector or {}):
            oobj._deleted = True
            has.append(oobj)
        for oobj in has:
            save(oobj)
        return has

    @staticmethod
    def types():
        assert Wd.workdir
        path = os.path.join(Wd.workdir, "store")
        if not os.path.exists(path):
            return []
        return sorted(os.listdir(path))


Class.add(Object)


def cdir(path):
    if os.path.exists(path):
        return
    if path.split(os.sep)[-1].count(":") == 2:
        path = os.path.dirname(path)
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)


def fntime(daystr):
    daystr = daystr.replace("_", ":")
    datestr = " ".join(daystr.split(os.sep)[-2:])
    datestr = datestr.split(".")[0]
    return time.mktime(time.strptime(datestr, "%Y-%m-%d %H:%M:%S"))


def locked(lock):

    def lockeddec(func, *args, **kwargs):
        def lockedfunc(*args, **kwargs):
            lock.acquire()
            res = None
            try:
                res = func(*args, **kwargs)
            finally:
                lock.release()
            return res

        lockeddec.__wrapped__ = func
        return lockedfunc

    return lockeddec


def spl(txt):
    try:
        res = txt.split(",")
    except (TypeError, ValueError):
        res = txt
    return [x for x in res if x]


@locked(dblock)
def fns(name, timed=None):
    if not name:
        return []
    assert Wd.workdir
    path = os.path.join(Wd.workdir, "store", name) + os.sep
    if not os.path.exists(path):
        return []
    res = []
    dpath = ""
    for rootdir, dirs, _files in os.walk(path, topdown=False):
        if dirs:
            dpath = sorted(dirs)[-1]
            if dpath.count("-") == 2:
                ddd = os.path.join(rootdir, dpath)
                fls = sorted(os.listdir(ddd))
                if fls:
                    opath = os.path.join(ddd, fls[-1])
                    if (
                        timed
                        and "from" in timed
                        and timed["from"]
                        and fntime(opath) < timed["from"]
                    ):
                        continue
                    if timed and timed.to and fntime(opath) > timed.to:
                        continue
                    res.append(opath)
    return sorted(res, key=fntime)


@locked(dblock)
def hook(hfn):
    if hfn.count(os.sep) > 3:
        oname = hfn.split(os.sep)[-4:]
    else:
        oname = hfn.split(os.sep)
    cname = oname[0]
    cls = Class.get(cname)
    if cls:
        oobj = cls()
    else:
        oobj = Object()
    fnm = os.sep.join(oname)
    load(oobj, fnm)
    return oobj


def listfiles(workdir):
    path = os.path.join(workdir, "store")
    if not os.path.exists(path):
        return []
    return sorted(os.listdir(path))


def find(name, selector=None, index=None, timed=None, names=None):
    dbs = Db()
    if not names:
        names = Class.full(name)
    for nme in names:
        for fnm, oobj in dbs.find(nme, selector, index, timed):
            yield fnm, oobj


def last(oobj):
    dbs = Db()
    path, _obj = dbs.lastfn(oobj.__otype__)
    if _obj:
        update(oobj, _obj)
    if path:
        splitted = path.split(os.sep)
        stp = os.sep.join(splitted[-4:])
        return stp
    return None


def scancls(mod):
    for _k, clz in inspect.getmembers(mod, inspect.isclass):
        Class.add(clz)
    return mod


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
