# This file is placed in the Public Domain.


"database tests"


import inspect
import os
import random
import shutil
import sys
import unittest


from gcid.object import Db, Object, all, dump, find, fns, fntime, load
from gcid.object import listfiles, hook, save


db = Db()
fn = "store/gcid.object.Object/61cba0b9-29c7-4154-a6c4-10b7365b3730/2022-04-11/22:40:31.259218"


class Test_Dbs(unittest.TestCase):


    def setUp(self):
        e = Object()
        e.txt = "test"
        save(e)

    def tearDown(self):
        db.remove("gcid.object.Object", {"txt": "test"})

    def test_Db(self):
        db = Db()
        self.assertTrue(type(db), Db)

    def test_Db_find(self):
        e = Object()
        e.txt = "test"
        save(e)
        res = db.find("gcid.object.Object")
        self.assertTrue(res)

    def test_Db_findselect(self):
        res = db.find("gcid.object.Object", {"txt": "test"})
        self.assertTrue(res)

    def test_Db_lastmatch(self):
        res = db.lastmatch("gcid.object.Object")
        self.assertTrue(res)

    def test_Db_lasttype(self):
        res = db.lasttype("gcid.object.Object")
        self.assertTrue(res)

    def test_Db_lastfn(self):
        res = db.lastfn("gcid.object.Object")
        self.assertTrue(res)

    def test_Db_remove(self):
        e = Object()
        e.txt = "test"
        save(e)
        res = db.remove("gcid.object.Object", {"txt": "test"})
        self.setUp()
        self.assertTrue(res)

    def test_types(self):
        res = db.types()
        self.assertTrue("gcid.object.Object" in res)

    def test_wrongfilename(self):
        fn, _o = db.lastfn("gcid.object.Object")
        shutil.copy(fn, fn + "bork")
        res = db.find("gcid.object.Object")
        self.assertTrue(res)

    def test_wrongfilename2(self):
        fntime(fn+"bork")

    def test_fntime(self):
        t = fntime(fn)
        self.assertEqual(t,  1649709631.259218)

    def test_fns(self):
        fs = fns("gcid.object.Object")
        self.assertTrue(fs)

    def test_hook(self):
        e = Object()
        e.txt = "test"
        p = save(e)
        o = hook(p)
        self.assertTrue("gcid.object.Object" in str(type(o)) and o.txt == "test")

    def test_listfiles(self):
        fns = listfiles(".test")
        self.assertTrue(fns)
        
    def test_all(self):
        fns = all()
        self.assertTrue(fns)

    def test_dump(self):
        e = Object()
        e.txt = "test"
        p = dump(e, ".test/store/%s" % e.__stp__)
        o = Object()
        load(o, p)
        self.assertEqual(o.txt, "test")

    def test_find(self):
        objs = find("gcid.object.Object", {"txt": "test"})
        self.assertTrue(objs)
