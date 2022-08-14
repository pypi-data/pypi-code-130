# This file is placed in the Public Domain.


"time tests"


import unittest


from gcid.timer import Timer


def test(event):
    pass


class Test_Time(unittest.TestCase):

    def test_timer(self):
        t = Timer(60, test)
        self.assertEqual(type(t), Timer)
