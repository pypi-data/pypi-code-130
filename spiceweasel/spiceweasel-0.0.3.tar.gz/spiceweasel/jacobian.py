# -*- coding: utf-8 -*-
##############################################
# The MIT License (MIT)
# Copyright (c) 2022 Kevin Walchko
# see LICENSE for full details
##############################################
import numpy as np
# from pyrk import RK4

class Jacobian:
    def __init__(self, f):
        self.f = f
        self.jac = None
        self.n = 0

    def check(self, x):
        if self.n == 0:
            self.n = len(x)
            self.jac = np.zeros((self.n, self.n))

# class JacobianForward(Jacobian):
#     def __call__(self, x, dx=1e-8):
#         # if self.n == 0:
#         self.check(x)
#             # self.n = len(x)
#             # self.jac = np.zeros((self.n, self.n))
#         func = self.f(x)

#         for j in range(self.n):
#             Dxj = (abs(x[j])*dx if x[j] != 0 else dx)
#             d = np.zeros(self.n)
#             d[j] = Dxj
#             self.jac[:, j] = (self.f(x+d) - func)/Dxj
#         return self.jac

class JacobianCenter(Jacobian):
    def __call__(self, t, x, u=None, dx=1e-8):
        self.check(x)

        for j in range(self.n):
            Dxj = (abs(x[j])*dx if x[j] != 0 else dx)
            d = np.zeros(self.n)
            d[j] = Dxj
            if u is None:
                self.jac[:, j] = (self.f(t, x+d) - self.f(t, x-d))/(2*Dxj)
            else:
                self.jac[:, j] = (self.f(t, x+d, u) - self.f(t, x-d, u))/(2*Dxj)
        return self.jac