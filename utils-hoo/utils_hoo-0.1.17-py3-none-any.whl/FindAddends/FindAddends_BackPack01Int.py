# -*- coding: utf-8 -*-

# 参考:
# https://blog.csdn.net/mandagod/article/details/79588753


import numpy as np


def FindAddends_BackPack01Int(tgt_sum, alts, F=None):
    '''
    从给定的列表alts（正数）中选取若干个数，其和小于等于tgt_sum并且最接近sum_tgt
    思路: 求和问题转化为物品价值和重量相等的01（正）整数背包问题
    缺点: 浪费空间

    Parameters
    ----------
    tgt_sum: 目标和
    alts: 备选加数列表
    F: 浮点数转化为整数时的乘数

    Returns
    -------
    max_v: 最近接tgt_sum的最大和
    trace: 和为max_v的备选数列表
    '''

    # 浮点数转化为整数
    F = 1 if F is None else F
    alts = [round(x*F) for x in alts]
    tgt_sum = round(tgt_sum*F)

    N = len(alts)
    values = np.zeros((tgt_sum + 1)) # 记录备选数之和的变化过程
    states = [] # states[_]=[i, j]表示在和为j的时候第i个备选数参与了求和

    # 背包求解
    for i in range(0, N):
        for j in range(tgt_sum, alts[i]-1, -1):
            tmp = values[j-alts[i]] + alts[i] # 假设和为j时加数中包含了第i个数
            if tmp > values[j]:
                values[j] = tmp
                states.append((i, j))

    max_v = values[-1] / F

    # 路径回溯
    i = N
    j = tgt_sum
    trace = []

    while i >= 0:
        if (i, j) in states:
            trace.append(alts[i]/F)
            j -= alts[i]
        i -= 1

    return max_v, trace


if __name__ == '__main__':
    tgt_sum = 22 + 13 + 7
    alts = [50, 22, 15, 22, 14, 13, 7, 100]
    F = None

    tgt_sum = 22 + 21 + 7.1
    alts = [22, 15, 14, 13, 7, 6.1, 5, 21.5, 100]
    F = 10

    max_v, trace = FindAddends_BackPack01Int(tgt_sum, alts, F=F)
    print('目标和:', tgt_sum)
    print('备选加数和:', max_v)
    print('备选加数:', trace)
