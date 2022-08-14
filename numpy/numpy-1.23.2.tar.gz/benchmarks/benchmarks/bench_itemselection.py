from __future__ import absolute_import, division, print_function

from .common import Benchmark, TYPES1

import numpy as np


class Take(Benchmark):
    params = [
        [(1000, 1), (1000, 2), (2, 1000, 1), (1000, 3)],
        ["raise", "wrap", "clip"],
        TYPES1]
    param_names = ["shape", "mode", "dtype"]

    def setup(self, shape, mode, dtype):
        self.arr = np.ones(shape, dtype)
        self.indices = np.arange(1000)

    def time_contiguous(self, shape, mode, dtype):
        self.arr.take(self.indices, axis=-2, mode=mode)


class PutMask(Benchmark):
    params = [
        [True, False],
        TYPES1]
    param_names = ["values_is_scalar", "dtype"]

    def setup(self, values_is_scalar, dtype):
        if values_is_scalar:
            self.vals = np.array(1., dtype=dtype)
        else:
            self.vals = np.ones(1000, dtype=dtype)

        self.arr = np.ones(1000, dtype=dtype)

        self.dense_mask = np.ones(1000, dtype="bool")
        self.sparse_mask = np.zeros(1000, dtype="bool")

    def time_dense(self, values_is_scalar, dtype):
        np.putmask(self.arr, self.dense_mask, self.vals)

    def time_sparse(self, values_is_scalar, dtype):
        np.putmask(self.arr, self.sparse_mask, self.vals)

