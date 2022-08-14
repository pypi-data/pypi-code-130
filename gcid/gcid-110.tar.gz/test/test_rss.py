# This file is placed in the Public Domain.


"rss tests"


import unittest


from gcid.rss import Fetcher


class Test_RSS(unittest.TestCase):

    def test_fetcher(self):
        f = Fetcher()
        self.assertEqual(type(f), Fetcher)
