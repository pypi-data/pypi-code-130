# -*- coding: utf-8 -*-

# 参考:
# https://my.oschina.net/u/3242615/blog/1940533/
# https://blog.csdn.net/qq_34178562/article/details/79959380


import numpy as np


def BackPack01_Int_Dy(c, v, w):
    '''
    动态规划解决（正）整数0-1背包问题
    缺点: 只能求解正整数情况

    Parameters
    ----------
    c: 背包最大容量
    v: 物品价值列表
    w: 物品重量列表

    Returns
    -------
    max_v: 最大价值
    trace: 最大价值解对应物品编号（从0开始计）
    v_mat: 完整价值矩阵
        注: v_mat[i, j]表示在总容量为j的情况下，
           在从第i至n（所有物品个数）个物品中选择物品放入时的最大价值
    '''

    if len(v) != len(w):
        raise Exception('需要保持v和w长度相等！')

    n = len(v)
    m = c + 1
    v_mat = np.zeros((n, m))

    # 填v_mat矩阵迭代过程
    # 装进第一件物品（这里从最后一件开装）
    for i in range(0, m):
        v_mat[-1, i] = v[-1] if i >= w[-1] else 0

    for i in range(n-2, -1, -1): # i遍历每件物品
        for j in range(0, m): # j从小到大遍历容器总容量
            # 若总容量小于重量，则不能装进去，只能保持原状
            if j < w[i]:
                v_mat[i, j] = v_mat[i+1, j]

            # 若总容量不小于重量，则可保持原状或加入（或置换）新物品
            else:
                v_mat[i, j] = max(v_mat[i+1, j], v_mat[i+1, j-w[i]] + v[i])

    max_v = v_mat[0, c]

    trace = traceBack(c, v, w, v_mat) # 溯源确定物品编号

    return max_v, trace, v_mat


def traceBack(c, v, w, v_mat):
    '''
    （正）整数0-1背包问题动态规划路径溯源

    Parameters
    ----------
    c: 背包最大容量
    v: 物品价值列表
    w: 物品重量列表
    v_mat: 完整价值矩阵

    Returns
    -------
    trace: 最优路径（最大价值对应物品编号列表，编号从0开始计）
    '''

    n = v_mat.shape[0]
    trace = []
    for i in range(0, n-1):
        if v_mat[i, c] == v_mat[i+1,c-w[i]] + v[i]: # 发生过置换或新装入物品操作
            c -= w[i]
            trace.append(i)

    # 第一个装入的物品
    i += 1
    if v_mat[i, c] == v[i]:
        trace.append(i)

    return trace


def BackPack01_Int_Dy_smp(c, v, w):
    '''
    动态规划解决（正）整数0-1背包问题，只输出最大价值，不考虑路径回溯
    缺点: 只能求解正整数情况

    Parameters
    ----------
    c: 背包最大容量
    v: 物品价值列表
    w: 物品重量列表

    Returns
    -------
    max_v: 最大价值
    values: 最大价值变化过程（相当于BackPack01_Int_Dy函数中v_mat的第一行）
        注: values[j]表示总容量为j的情况下可装物品的最大价值
    '''

    if len(v) != len(w):
        raise Exception('需要保持v和w长度相等！')

    n = len(v)
    m = c + 1

    values = [0 for i in range(m)]

    # 填values迭代过程
    # 在BackPack01_Int_Dy上改进，通过尾部迭代，每轮迭代(i)中，values只保存最佳结果
    # 从而降低空间复杂度
    for i in range(0, n): # i遍历每件物品
        for j in range(c, 0, -1): # j从大到小遍历容器总容量
            # 若可装进i(总容量不小于重量)，则可保持原状或加入（或置换）新物品
            if j >= w[i]:
                values[j] = max(values[j-w[i]] + v[i], values[j])

    return values[-1]


def BackPack01_Float_Dy(c, v, w, F=100):
    '''
    利用整数方法通过乘数F改造解决浮点数背包问题
    F为浮点数转化为整数时的乘数
    缺点: 浪费空间
    '''
    c = round(c * F)
    v = [round(x * F) for x in v]
    w = [round(x * F) for x in w]
    max_v, trace, v_mat = BackPack01_Int_Dy(c, v, w)
    return max_v/F, trace, v_mat/F


def BackPack01_Float_Dy_smp(c, v, w, F=100):
    '''
    利用整数方法通过乘数F改造解决浮点数背包问题，只输出最大价值，不考虑路径回溯
    F为浮点数转化为整数时的乘数
    '''
    c = round(c * F)
    v = [round(x * F) for x in v]
    w = [round(x * F) for x in w]
    max_v = BackPack01_Int_Dy_smp(c, v, w)
    return max_v/F


if __name__ == '__main__':
    #--------------------------------------------------------------------------
    # c = 10
    # v = [6, 3, 5, 4, 6]
    # w = [2, 2, 6, 5, 4]

    c = 9
    v = [1, 1, 7, 6]
    w = [2, 2, 4, 4]

    max_v = BackPack01_Int_Dy_smp(c, v, w)
    print('最大价值smp:', max_v)

    max_v, trace, v_mat = BackPack01_Int_Dy(c, v, w)
    print('最大价值:', max_v)
    print('最大重量:', sum([w[x] for x in trace]))
    print('最大价值对应物品编号:', trace)
    print('最大价值对应物品重量:', [w[x] for x in trace])
    print('最大价值对应物品价值:', [v[x] for x in trace])


    #--------------------------------------------------------------------------
    c = 10.2
    v = [2, 3, 1, 5, 4.2, 3]
    w = [2, 2, 3, 1.2, 5, 2]

    # c = 22 + 21 + 1.1
    # v = [22, 15, 14, 13, 7, 6.1, 5, 21.5, 100]
    # w = [22, 15, 14, 13, 7, 6.1, 5, 21.5, 100]

    max_v = BackPack01_Float_Dy_smp(c, v, w, F=10)
    print('最大价值smp:', max_v)

    max_v, trace, v_mat = BackPack01_Float_Dy(c, v, w, F=10)
    print('最大价值:', max_v)
    print('最大重量:', sum([w[x] for x in trace]))
    print('最大价值对应物品编号:', trace)
    print('最大价值对应物品重量:', [w[x] for x in trace])
    print('最大价值对应物品价值:', [v[x] for x in trace])
