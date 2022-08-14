# This file is placed in the Public Domain.


"bus"


import unittest


from genocide.hdl import Bus, Client


class TestBus(unittest.TestCase):

    def test_construct(self):
        bus = Bus()
        self.assertEqual(type(bus), Bus)

    def test_add(self):
        bus = Bus()
        clt = Client()
        bus.add(clt)
        self.assertTrue(clt in bus.objs)

    def test_announce(self):
        bus = Bus()
        clt = Client()
        bus.add(clt)
        bus.announce("test")
        self.assertTrue(clt.gotcha)

    def test_byorig(self):
        bus = Bus()
        clt = Client()
        bus.add(clt)
        self.assertEqual(bus.byorig(clt.orig), clt)

    def test_say(self):
        bus = Bus()
        clt = Client()
        bus.add(clt)
        bus.say(clt.orig, "#test", "test")
        self.assertTrue(clt.gotcha)
