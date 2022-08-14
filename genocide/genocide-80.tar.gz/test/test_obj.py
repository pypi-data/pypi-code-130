# pylint: disable=E1101,C0116
# This file is placed in the Public Domain.


"object"


import os
import unittest


from genocide.obj import Db, Wd, cdir, fns, hook, last
from genocide.obj import Object, edit, get, items, keys, save, update, values
from genocide.obj import dumps, load, loads, printable, register


import genocide.obj


Wd.workdir = ".test"


attrs1 = (
        'Class',
        'Db',
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
        'find',
        'fntime',
        'get',
        'items',
        'keys',
        'last',
        'lastfromkeys',
        'load',
        'loads',
        'matchkey',
        'pop',
        'popitem',
        'printable',
        'read',
        "register",
        'save',
        'search',
        'setdefault',
        'update',
        'values'
)


attrs2 = (
    '__class__',
    '__class_getitem__',
    '__contains__',
    '__delattr__',
    '__delitem__',
    '__dict__',
    '__dir__',
    '__doc__',
    '__eq__',
    '__format__',
    '__ge__',
    '__getattribute__',
    '__getitem__',
    '__gt__',
    '__hash__',
    '__init__',
    '__init_subclass__',
    '__ior__',
    '__iter__',
    '__le__',
    '__len__',
    '__lt__',
    '__module__',
    '__ne__',
    '__new__',
    '__oqn__',
    '__otype__',
    '__reduce__',
    '__reduce_ex__',
    '__repr__',
    '__reversed__',
    '__ror__',
    '__setattr__',
    '__setitem__',
    '__sizeof__',
    '__slots__',
    '__stp__',
    '__str__',
    '__subclasshook__'
)


VALIDJSON = '{"test": "bla"}'


class Composite(Object):

    def __init__(self):
        super().__init__()
        self.dbs = Db()


class TestObject(unittest.TestCase):

    def test_constructor(self):
        obj = Object()
        self.assertTrue(type(obj), Object)

    def test_import(self):
        self.assertEqual(tuple(dir(genocide.obj)), attrs1)

    def test_attributes(self):
        obj = Object()
        self.assertEqual(tuple(dir(obj)), attrs2)

    def test__class(self):
        obj = Object()
        clz = obj.__class__()
        self.assertTrue("Object" in str(type(clz)))

    def test_contains(self):
        obj = Object()
        obj.key = "value"
        self.assertTrue("key" in obj)

    def test_delattr(self):
        obj = Object()
        obj.key = "value"
        obj.__delattr__("key")
        self.assertTrue("key" not in obj)

    def test_delitem(self):
        obj = Object()
        obj["key"] = "value"
        obj.__delitem__("key")
        self.assertTrue("key" not in obj)

    def test_dict(self):
        obj = Object()
        self.assertEqual(obj.__dict__, {})

    def test_dir(self):
        obj = Object()
        self.assertEqual(
            dir(obj), list(attrs2)
        )

    def test_doc(self):
        obj = Object()
        self.assertEqual(obj.__doc__, "object")

    def test_eq(self):
        obj = Object()
        oobj = Object()
        self.assertTrue(obj == oobj)

    def test_format(self):
        obj = Object()
        self.assertEqual(obj.__format__(""), "{}")

    def test_ge(self):
        oobj1 = Object()
        oobj2 = Object()
        oobj2.key = "value"
        self.assertTrue(oobj2 >= oobj1)

    def test_getattribute(self):
        obj = Object()
        obj.key = "value"
        self.assertEqual(obj.__getattribute__("key"), "value")

    def test_getitem(self):
        obj = update(Object(), {"key": "value"})
        self.assertEqual(obj.__getitem__("key"), "value")

    def test_gt(self):
        obj = Object()
        oobj = Object()
        oobj.key = "value"
        self.assertTrue(oobj > obj)

    def test_hash__(self):
        obj = Object()
        hsj = hash(obj)
        self.assertTrue(isinstance(hsj, int))

    def test_init(self):
        obj = Object()
        self.assertTrue(type(Object.__init__(obj)), Object)

    def test_init_subclass(self):
        obj = Object()
        scls = obj.__init_subclass__()
        self.assertEqual(scls, None)

    def test_iter(self):
        obj = Object()
        obj.key = "value"
        self.assertTrue(
            list(obj.__iter__()),
            [
                "key",
            ],
        )

    def test_le(self):
        obj = Object()
        oobj = Object()
        oobj.key = "value"
        self.assertTrue(obj <= oobj)

    def test_len(self):
        obj = Object()
        self.assertEqual(len(obj), 0)

    def test_lt(self):
        obj = Object()
        oobj = Object()
        oobj.key = "value"
        self.assertTrue(obj < oobj)

    def test_module(self):
        self.assertTrue(Object().__module__, "genocide.obj")

    def test_ne(self):
        obj = Object()
        oobj = Object()
        oobj.key = "value"
        self.assertTrue(obj != oobj)

    def test_new(self):
        obj = Object()
        oobj = obj.__new__(Object)
        self.assertEqual(obj, oobj)

    def test_otype(self):
        self.assertEqual(Object().__otype__, "genocide.obj.Object")

    def test_reduce(self):
        obj = Object()
        obj.__reduce__()
        self.assertTrue("obj" in str(type(obj)))

    def test_reduce_ex(self):
        obj = Object()
        obj.__reduce_ex__("test")
        self.assertTrue("obj" in str(type(obj)))

    def test_repr(self):
        self.assertTrue(update(Object(),
                               {"key": "value"}).__repr__(), {"key": "value"})

    def test_setattr(self):
        obj = Object()
        obj.__setattr__("key", "value")
        self.assertTrue(obj.key, "value")

    def test_setitem(self):
        obj = Object()
        obj.__setitem__("key", "value")
        self.assertTrue(obj["key"], "value")

    def test_setitem2(self):
        obj = Object()
        obj.__setitem__("key", "value")
        self.assertTrue(obj.key, "value")

    def test_sizeof(self):
        self.assertEqual(Object().__sizeof__(), 40)

    def test_slots(self):
        self.assertEqual(Object().__slots__, ("__dict__",
                                              "__otype__",
                                              "__stp__"))

    def test_stp(self):
        obj = Object()
        self.assertTrue("genocide.obj.Object" in obj.__stp__)

    def test_str(self):
        obj = Object()
        self.assertEqual(str(obj), "{}")

    def test_subclasshook(self):
        obj = Object()
        bus = obj.__subclasshook__()
        self.assertEqual(bus, NotImplemented)

    def test_dbs(self):
        dbs = Db()
        self.assertTrue(type(dbs), Db)

    def test_cdir(self):
        cdir(".test")
        self.assertTrue(os.path.exists(".test"))

    def test_composite(self):
        com1 = Composite()
        com2 = loads(dumps(com1))
        self.assertEqual(type(com2.dbs), type({}))

    def test_edit(self):
        obj = Object()
        dta = {"key": "value"}
        edit(obj, dta)
        self.assertEqual(obj.key, "value")

    def test_printable(self):
        obj = Object()
        self.assertEqual(printable(obj), "")

    def test_fns(self):
        Wd.workdir = ".test"
        obj = Object()
        save(obj)
        self.assertTrue("Object" in fns("genocide.obj.Object")[0])

    def test_get(self):
        obj = Object()
        obj.key = "value"
        self.assertEqual(get(obj, "key"), "value")

    def test_hook(self):
        obj = Object()
        obj.key = "value"
        pth = save(obj)
        oobj = hook(pth)
        self.assertEqual(oobj.key, "value")

    def test_keys(self):
        obj = Object()
        obj.key = "value"
        self.assertEqual(
            list(keys(obj)),
            [
                "key",
            ],
        )

    def test_items(self):
        obj = Object()
        obj.key = "value"
        self.assertEqual(
            list(items(obj)),
            [
                ("key", "value"),
            ],
        )

    def test_json(self):
        obj = Object()
        obj.test = "bla"
        oobj = loads(dumps(obj))
        self.assertEqual(oobj.test, "bla")

    def test_jsondump(self):
        obj = Object()
        obj.test = "bla"
        self.assertEqual(dumps(obj), VALIDJSON)


    def test_last(self):
        oobj = Object()
        oobj.key = "value"
        save(oobj)
        last(oobj)
        self.assertEqual(oobj.key, "value")

    def test_load(self):
        obj = Object()
        obj.key = "value"
        pld = save(obj)
        oobj = Object()
        load(oobj, pld)
        self.assertEqual(oobj.key, "value")

    def test_register(self):
        obj = Object()
        register(obj, "key", "value")
        self.assertEqual(obj.key, "value")

    def test_save(self):
        Wd.workdir = ".test"
        obj = Object()
        path = save(obj)
        self.assertTrue(os.path.exists(os.path.join(Wd.workdir,
                                                    "store",
                                                    path
                                                   )))

    def test_update(self):
        obj = Object()
        obj.key = "value"
        oobj = Object()
        update(oobj, obj)
        self.assertTrue(oobj.key, "value")

    def test_values(self):
        obj = Object()
        obj.key = "value"
        self.assertEqual(
            list(values(obj)),
            [
                "value",
            ],
        )
