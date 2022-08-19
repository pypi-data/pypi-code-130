import unittest
import numpy as np

import AutoFeedback.funcchecks as fc


def f2(x):
    return


def f4(x):
    return x**2


def f3(x, y):
    return(np.sqrt(f4(x)))


class UnitTests(unittest.TestCase):
    def test_exists(self):
        assert(fc._exists('f1'))

    def test_notexists(self):
        assert(not fc._exists('f3'))

    def test_1input_vars(self):
        assert(fc._input_vars(f4, 10))

    def test_2input_vars(self):
        assert(fc._input_vars(f3, (10, 11)))

    def test_not1input_vars(self):
        assert(not fc._input_vars(f3, (10, 11, 12)))

    def test_not2input_vars(self):
        assert(not fc._input_vars(f4, (10, 11)))

    def test_returns(self):
        assert(fc._returns(f3, (10, 11)))

    def test_notreturns(self):
        assert(not fc._returns(f2, (10)))

    def test_check_outputs(self):
        assert(fc._check_outputs(f4, (4,), 16))

    def test_2check_outputs(self):
        assert(fc._check_outputs(f4, (-10,), 100))

    def test_array_check_outputs(self):
        assert(fc._check_outputs(f4, (np.array([1, 2, 3]),), [1, 4, 9]))

    def test_notcheck_outputs1(self):
        assert(not fc._check_outputs(f4, (3,), 10))

    def test_notcheck_outputs2(self):
        assert(not fc._check_outputs(f3, (10, 11), 9))

    def test_calls(self):
        assert(fc._check_calls(f3, 'f4'))

    def test_notcalls(self):
        assert(not fc._check_calls(f3, 'f1'))


class SystemTests(unittest.TestCase):
    def test_f1(self):
        assert (fc.check_func('f1', [(3,), (-4,)], [9, 16],
                              output=False) and
                not fc.check_func('f2', [(3,), (-4,)], [9, 16],
                                  output=False))
