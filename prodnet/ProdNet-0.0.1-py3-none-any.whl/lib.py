""" This module contains all helper functions not core to the models.
"""
import numpy as np
from numba import njit


def pmf(a):
    x, counts = np.unique(a, return_counts=True)
    return x, counts/len(a)
  

def cdf(a, start=0):
    x, counts = np.unique(a, return_counts=True)
    cusum = np.cumsum(counts) + start
    y = cusum / cusum[-1]
    x = np.insert(x, 0, x[0])
    y = np.insert(y, 0, start / cusum[-1])
    return x, y


def icdf(a):
    x, counts = np.unique(a, return_counts=True)
    cusum = np.cumsum(counts)
    y = 1 - cusum / cusum[-1]
    y = np.insert(y, 0, 1)
    return x, y[:-1]


@njit
def faster_dot(ind, ptr, dat, v, dtype):
    res = np.zeros(len(ptr)-1, dtype=dtype)
    for j in range(len(v)):
        if v[j] != 0:
            rows = ind[ptr[j]:ptr[j+1]]
            for n in range(len(rows)):
                res[rows[n]] += v[j]*dat[ptr[j]+n]

    return res
