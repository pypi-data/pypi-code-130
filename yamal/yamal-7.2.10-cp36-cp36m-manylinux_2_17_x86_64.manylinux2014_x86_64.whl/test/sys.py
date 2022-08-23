"""
        COPYRIGHT (c) 2022 by Featuremine Corporation.
        This software has been provided pursuant to a License Agreement
        containing restrictions on its use.  This software contains
        valuable trade secrets and proprietary information of
        Featuremine Corporation and is protected by law.  It may not be
        copied or distributed in any form or medium, disclosed to third
        parties, reverse engineered or used in any manner not provided
        for in said License Agreement except with the prior written
        authorization from Featuremine Corporation.
"""

import unittest
import os
import tempfile
import yamal
from yamal import modules, Reactor

testoutput = os.path.join(tempfile.gettempdir(), "testoutput.txt")
yamal.sys.path += [os.path.dirname(yamal.__file__)]


class TestLoadModule(unittest.TestCase):
    def test_load_module_success(self):
        testcomp = modules.testmodule.testcomponent

        try:
            os.remove(testoutput)
        except OSError:
            pass

        reactor = Reactor()
        comp = testcomp(
            reactor,
            filename=testoutput,
            none=None,
            int64=3,
            boolean=True,
            float64=4.5,
            sect={"int64": 2},
            arr=[])

        reactor.run(live=False)

        reactor = None
        comp = None

        with open(testoutput) as f:
            self.assertEqual(f.readline(), "0\n")
            self.assertEqual(f.readline(), "1\n")
            self.assertEqual(f.readline(), "2\n")
            self.assertEqual(f.readline(), "3\n")
            self.assertEqual(f.readline(), "4\n")
            self.assertEqual(f.readline(), "")

    def test_load_module_notfound(self):
        with self.assertRaisesRegex(RuntimeError, 'component module testmodule2 was not found') as cm:
            testcomp = modules.testmodule2.testcomponent
            reactor = Reactor()
            comp = testcomp(
                reactor,
                none=None,
                int64=3,
                boolean=True,
                float64=4.5,
                filename=testoutput,
                sect={"int64": 2},
                arr=[])

    def test_load_module_invalid_config(self):
        testcomp = modules.testmodule.testcomponent
        with self.assertRaisesRegex(RuntimeError, 'config error: missing required field int64') as cm:
            reactor = Reactor()
            comp = testcomp(
                reactor,
                none=None,
                #int64=3,
                boolean=True,
                float64=4.5,
                filename=testoutput,
                sect={"int64": 2},
                arr=[])

    def test_load_module_optional_field(self):
        testcomp = modules.testmodule.testcomponent
        reactor = Reactor()
        comp = testcomp(
            reactor,
            none=None,
            int64=3,
            boolean=True,
            #float64=4.5,
            filename=testoutput,
            sect={"int64": 2},
            arr=[])

    def test_comp_invalid_reactor(self):
        testcomp = modules.testmodule.testcomponent
        with self.assertRaisesRegex(RuntimeError, 'invalid reactor type') as cm:
            comp = testcomp(
                modules.testmodule,
                none=None,
                int64=3,
                boolean=True,
                float64=4.5,
                filename=testoutput,
                sect={"int64": 2},
                arr=[])

if __name__ == '__main__':
    unittest.main()
