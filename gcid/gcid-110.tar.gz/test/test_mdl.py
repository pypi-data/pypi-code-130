# This file is placed in the Public Domain.


"model tests"


import unittest


from gcid.model import oorzaak
from gcid.object import Object


class Test_Composite(unittest.TestCase):

    def test_composite(self):
        self.assertEqual(type(oorzaak), Object)
