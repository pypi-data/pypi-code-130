# -*- coding: utf-8 -*-
"""
Created on Thu Nov 25 22:38:48 2021

@author: Administrator
"""

import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize as optimize
pi = np.pi

# 模拟生成一组实验数据
x = np.arange(0, 10, 0.2)
y = -0.5 * np.cos(1.1 * x) + 0.5
noise = np.random.uniform(0, 0.1, len(x))
y += noise

y=aa
x=range(len(y))

fig, ax = plt.subplots()
ax.plot(x, y, 'b--')


def target_func(x, a0, a1, a2, a3):
    return a0 * np.sin(a1 * x + a2) + a3

# 拟合sin曲线
fs = np.fft.fftfreq(len(x), x[1] - x[0])
Y = abs(np.fft.fft(y))
freq = abs(fs[np.argmax(Y[1:]) + 1])
a0 = max(y) - min(y)
a1 = 2 * pi * freq
a2 = 0
a3 = np.mean(y)
p0 = [a0, a1, a2, a3]
para, _ = optimize.curve_fit(target_func, x, y, p0=p0)
print(para)
y_fit = [target_func(a, *para) for a in x]
ax.plot(x, y_fit, 'g')

plt.show()
