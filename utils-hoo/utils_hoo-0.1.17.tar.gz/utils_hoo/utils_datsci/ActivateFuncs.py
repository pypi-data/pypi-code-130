# -*- coding: utf-8 -*-

import numpy as np


def sigmoid(x):
    '''sigmoid激活函数'''
    return 1.0 / (1 + np.exp(-x))


def softmax(x, _max=False):
    '''softmax函数，x为array或list或pd.Series'''
    x = np.array(x)
    if _max:
        x = x - x.max()
    x_exp = np.exp(x)
    return x_exp / x_exp.sum()


def softmax2(X, axis=0, _max=False):
    '''
    softmax函数
    x是二维的array或list或dataframe
    # https://www.cnblogs.com/ysugyl/p/12922598.html
    '''
    X = np.array(X)
    assert(len(X.shape) == 2)
    if _max:
        Xmax = X.max(axis=axis)
        if axis == 0:
            X = X - Xmax
        elif axis == 1:
            X = X - Xmax.reshape(-1, 1)
    X_exp = np.exp(X)
    X_soft = X_exp / X_exp.sum(axis=axis, keepdims=True)
    return X_soft


def softplus(x):
    '''softplus激活函数 '''
    return np.log(1 + np.exp(x))


def tanh(x):
    '''tanh激活函数'''
    return (np.exp(x) - np.exp(-x)) / (np.exp(x) + np.exp(-x))
