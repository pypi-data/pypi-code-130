# This file is placed in the Public Domain.


"path tests"


import unittest


from gcid.object import fntime


fn = "store/gcid.evt.Event/61cba0b9-29c7-4154-a6c4-10b7365b3730/2022-04-11/22:40:31.259218"


class Test_Path(unittest.TestCase):


    def test_path(self):
        t = fntime(fn)
        self.assertEqual(t, 1649709631.259218)
