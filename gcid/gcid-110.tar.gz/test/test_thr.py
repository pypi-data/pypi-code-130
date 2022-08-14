# This file is placed in the Public Domain.


"threads tests"


import unittest


from gcid.handler import Thread


def test(event):
     pass


class Test_Threads(unittest.TestCase):

    def test_thread(self):
        t = Thread(test, "test")
        self.assertEqual(type(t), Thread)
