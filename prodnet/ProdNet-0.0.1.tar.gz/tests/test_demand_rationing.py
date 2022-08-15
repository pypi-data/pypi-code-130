
""" Test graph ensemble model classes on simple sample graph. """
import ProdNet as pn
import numpy as np
import pytest
from numpy.random import default_rng
from hypothesis import given
from hypothesis.strategies import floats
from hypothesis.extra.numpy import arrays


# Define global variables for multiple tests
N = 4
T = 1
O = np.array([[1, 2, 3, 4],
              [5, 6, 7, 8],
              [9, 8, 7, 6],
              [5, 4, 3, 2]])
C = np.array([1, 2, 1, 2])
P = np.ones(N)


class TestProportionalRationing():
    # Initialize model with proportional rationing
    model = pn.SimEngine(T, N, rationing_type='proportional')

    def test_dimensions(self):
        # Ensure dimensions respect original
        z, c_a = pn.SimEngine.prop_rationing(O, P, C)
        assert z.shape == (N, N)
        assert c_a.shape == (N,)

    def test_inconsistent_dimensions(self):
        # Ensure dimensions respect original
        o = np.ones((N - 1, N - 1))
        msg = 'Intermediate orders is not a NxN matrix.'
        with pytest.raises(ValueError, match=msg):
            z, c_a = self.model.demand_rationing(o, P, C)
        p = np.ones(N + 1)
        msg = 'Production is not a N-length vector.'
        with pytest.raises(ValueError, match=msg):
            z, c_a = self.model.demand_rationing(O, p, C)
        c = np.ones(N - 2)
        msg = 'Consumption is not a N-length vector.'
        with pytest.raises(ValueError, match=msg):
            z, c_a = self.model.demand_rationing(O, P, c)

    def test_zero_production(self):
        # Let p = o, then all demand should be zero
        p = np.zeros(N)
        z, c_a = pn.SimEngine.prop_rationing(O, p, C)
        assert np.all(z == 0)
        assert np.all(c_a == 0)

    def test_unit_demand(self):
        # Let p = 1, then all demand should be value/tot_demand
        z, c_a = pn.SimEngine.prop_rationing(O, P, C)
        exp_z = np.array([[1/11, 2/11, 3/11, 4/11],
                          [5/28, 6/28, 7/28, 8/28],
                          [9/31, 8/31, 7/31, 6/31],
                          [5/16, 4/16, 3/16, 2/16]])
        exp_c_a = np.array([1/11, 2/28, 1/31, 2/16])
        assert np.allclose(z, exp_z)
        assert np.allclose(c_a, exp_c_a)

    @given(arrays(dtype='f8', shape=(N, N), 
                  elements=floats(min_value=0, max_value=1e20,
                                  allow_nan=False, allow_infinity=False)),
           arrays(dtype='f8', shape=N,
                  elements=floats(min_value=0, max_value=1e20,
                                  allow_nan=False, allow_infinity=False)),
           arrays(dtype='f8', shape=N,
                  elements=floats(min_value=0, max_value=1e20,
                                  allow_nan=False, allow_infinity=False)),)
    def test_random_entries(self, o, p, c):
        z, c_a = pn.SimEngine.prop_rationing(o, p, c)
        # Check all values must be positive
        assert np.all(z >= 0)
        assert np.all(c_a >= 0)
        # Check that the sum of z and c_a equals the production level or total
        # demand
        assert np.all(np.isclose(z.sum(axis=1) + c_a, p) |
                      np.isclose(z.sum(axis=1) + c_a, o.sum(axis=1) + c))
        # Check that no element of z or c_a is greater than the orders received
        assert np.all(z <= o)
        assert np.all(c_a <= c)

    def test_negative_entries(self):
        # Ensure that an error is raised if any entry is negative
        o = O.copy()
        o[1, 2] = -12
        msg = 'Negative orders, production, or demand is not allowed.'
        with pytest.raises(ValueError, match=msg):
            z, c_a = self.model.demand_rationing(o, P, C)
        p = P.copy()
        p[1] = -1
        with pytest.raises(ValueError, match=msg):
            z, c_a = self.model.demand_rationing(O, p, C)
        c = C.copy()
        c[2] = -4
        with pytest.raises(ValueError, match=msg):
            z, c_a = self.model.demand_rationing(O, P, c)
