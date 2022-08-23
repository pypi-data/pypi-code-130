# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
from scipy.stats import norm
from math import log, sqrt, exp
from utils_hoo import plot_Series


# 看涨/看跌简称列表
call_names = ['c', 'call', '看涨', '看多', '多', '做多', '认购']
put_names = ['p', 'put', '看跌', '看空', '空', '做空', '认沽']


def BS_opt(Pnow, Pexe, D, r=3/100, sigma=22.5/100, i_d=0, D_year=365):
    '''
    BS期权定价公式

    Parameters
    ----------
    Pnow: 标的现价
    Pexe: 标的执行价
    D: 剩余天数
    r: 无风险利率，年化
    sigma: 波动率（目标标的收益波动率，年化）？
    i_d: 隐含分红率？
    D_year: 一年天数，默认为365，即自然天数（也可以只考虑交易天数）

    Returns
    -------
    Popt_call: 认购做多期权合约价格
    Popt_put: 认沽做空期权合约价格

    参考：
    https://www.optionseducation.org/toolsoptionquotes/optionscalculator
    http://www.rmmsoft.com.cn/RSPages/onlinetools/OptionAnalysis/OptionAnalysisCN.aspx
    https://blog.csdn.net/qq_41239584/article/details/83383780
    https://zhuanlan.zhihu.com/p/38293827
    https://zhuanlan.zhihu.com/p/38294971
    https://zhuanlan.zhihu.com/p/96431951
    https://zhuanlan.zhihu.com/p/142685333（隐含分红率）
    https://github.com/caly5144/shu-s-project/tree/master/options
    '''

    T = D / D_year

    d1 = (log(Pnow / Pexe) + (r - i_d + 0.5 * sigma ** 2) * T) / (sigma * sqrt(T))
    # d2 = (log(Pnow / Pexe) + (r - i_d - 0.5 * sigma ** 2) * T) / (sigma * sqrt(T))
    d2 = d1 - sigma * sqrt(T)

    # 看涨
    Popt_call = Pnow * exp(-i_d * T) * norm.cdf(d1) - Pexe * exp(-r * T) * norm.cdf(d2)
    # 看跌
    Popt_put = Pexe * exp(-r * T) * norm.cdf(-d2) - Pnow * exp(-i_d * T) * norm.cdf(-d1)

    return Popt_call, Popt_put


def MCBS_opt(Pnow, Pexe, D, r=3/100, sigma=22.5/100, D_year=365,
             D_cut=60, N_mc=500000, random_seed=62, kwargs_plot=None):
    '''
    注：没考虑分红！
    MC-BS，蒙特卡罗模拟BS公式计算期权价格

    Parameters
    ----------
    Pnow: 标的现价
    Pexe: 标的执行价
    D: 剩余天数
    r: 无风险利率，年化
    sigma: 波动率（目标标的收益波动率，年化）
    D_year: 一年天数，默认为365，即自然天数（也可以只考虑交易天数）
    D_cut: 将剩余到期时间划分为D_cut个小时段
    N_mc: 蒙特卡罗模拟次数
    random_seed: 随机数种子

    Returns
    -------
    Popt_call: 认购做多期权合约价格
    Popt_put: 认沽做空期权合约价格

    参考：
    https://blog.csdn.net/qwop446/article/details/88914401
    https://blog.csdn.net/hzk427/article/details/104538974
    '''

    np.random.seed(random_seed)

    T = D / D_year
    dt = T / D_cut

    P = np.zeros((D_cut+1, N_mc)) # 模拟价格
    P[0] = Pnow
    for t in range(1, D_cut+1):
        db = np.random.standard_normal(N_mc) # 布朗运动随机游走
        P[t] = P[t-1] * np.exp((r - 0.5 * sigma ** 2) * dt + \
                                                        sigma * sqrt(dt) * db)

    if not kwargs_plot is None:
        df_plot = pd.DataFrame(P)
        plot_Series(df_plot, {x: ('-', False) for x in df_plot.columns},
                    **kwargs_plot)

    # 看涨
    Popt_call = exp(-r * T) * np.sum(np.maximum(P[-1] - Pexe, 0)) / N_mc
    # 看跌
    Popt_put = exp(-r * T) * np.sum(np.maximum(Pexe - P[-1], 0)) / N_mc

    return Popt_call, Popt_put


def MCBSlog_opt(Pnow, Pexe, D, r=3/100, sigma=22.5/100, D_year=365,
                D_cut=60, N_mc=500000, random_seed=62, kwargs_plot=None):
    '''
    注：没考虑分红！
    MC-BS，蒙特卡罗模拟BS公式计算期权价格，对数格式

    Parameters
    ----------
    Pnow: 标的现价
    Pexe: 标的执行价
    D: 剩余天数
    r: 无风险利率，年化
    sigma: 波动率（目标标的收益波动率，年化）
    D_year: 一年天数，默认为365，即自然天数（也可以只考虑交易天数）
    D_cut: 将剩余到期时间划分为D_cut个小时段
    N_mc: 蒙特卡罗模拟次数
    random_seed: 随机数种子

    Returns
    -------
    Popt_call: 认购做多期权合约价格
    Popt_put: 认沽做空期权合约价格

    参考：
    https://blog.csdn.net/qwop446/article/details/88914401
    https://blog.csdn.net/hzk427/article/details/104538974
    '''

    np.random.seed(random_seed)

    T = D / D_year
    dt = T / D_cut

    dbs = np.random.standard_normal((D_cut+1, N_mc)) # 布朗运动随机游走
    dbs = np.cumsum((r - 0.5 * sigma**2) * dt + sigma * sqrt(dt) * dbs, axis=0)
    P = Pnow * np.exp(dbs) # 模拟价格

    if not kwargs_plot is None:
        df_plot = pd.DataFrame(P)
        plot_Series(df_plot, {x: ('-', False) for x in df_plot.columns},
                    **kwargs_plot)

    # 看涨
    Popt_call = exp(-r * T) * np.sum(np.maximum(P[-1] - Pexe, 0)) / N_mc
    # 看跌
    Popt_put = exp(-r * T) * np.sum(np.maximum(Pexe - P[-1], 0)) / N_mc

    return Popt_call, Popt_put


def BOPM_european(Pnow, Pexe, D, r=3/100, sigma=22.5/100, D_year=365,
                  D_cut=60):
    '''
    注：没考虑分红！
    二叉树欧式期权定价模型（BOP/CRR）

    Parameters
    ----------
    Pnow: 标的现价
    Pexe: 标的执行价
    D: 剩余天数
    r: 无风险利率，年化
    sigma: 波动率（目标标的收益波动率，年化）
    D_year: 一年天数，默认为365，即自然天数（也可以只考虑交易天数）
    D_cut: 将剩余到期时间划分为D_cut个小时段

    Returns
    -------
    Popt_call: 认购做多期权合约价格
    Popt_put: 认沽做空期权合约价格

    参考：
        https://zhuanlan.zhihu.com/p/62031783
        https://wiki.mbalib.com/wiki/二项期权定价模型
    '''

    T = D / D_year
    dt = T / D_cut
    df = exp(-r * dt) # discount per interval？

    # 计算u，d，p
    u = exp(sigma * sqrt(dt)) # up movement
    d = 1 / u # down movement
    p = (exp(r * dt) - d) / (u - d) # martingale branch probability

    # 二叉树
    mu = np.arange(D_cut + 1)
    mu = np.resize(mu, (D_cut + 1, D_cut + 1))
    md = np.transpose(mu)
    mu = u ** (mu - md)
    md = d ** md

    # 计算各节点的股票价格
    P = Pnow * mu * md

    # 计算叶子结点的期权价值
    Vcal = np.maximum(P-Pexe, 0) # 看涨期权
    Vput = np.maximum(Pexe-P, 0) # 看跌期权

    # 逐步向前加权平均并折现，得到期初期权价值
    for k in range(0, D_cut):
        # 逐列更新期权价值，相当于二叉树中的逐层向前折算
        Vcal[0:D_cut-k, D_cut-k-1] = \
                        (p * Vcal[0:D_cut - k, D_cut - k] + \
                         (1 - p) * Vcal[1:D_cut - k + 1, D_cut - k]) * df
        Vput[0:D_cut-k, D_cut-k-1] = \
                        (p * Vput[0:D_cut - k, D_cut - k] + \
                         (1 - p) * Vput[1:D_cut - k + 1, D_cut - k]) * df

    return Vcal[0, 0], Vput[0, 0]


# # CRR美式期权
# def BOPM_american(Pnow, K, T, r, sigma, otype, M=4):
#     '''
#     注：没考虑分红！
#     二叉树美式期权定价模型（BOP/CRR）

#     Parameters
#     ----------
#     Pnow : float
#         stock/index level at time 0
#     K : float
#         strike price
#     T : float
#         date of maturity
#     r : float
#         constant, risk-less short rate
#     sigma : float
#         volatility
#     otype : string
#         either 'call' or 'put'
#     M : int
#         number of time intervals

#     Returns
#     -------
#     Popt_call: 认购做多期权合约价格
#     Popt_put: 认沽做空期权合约价格

#     参考：
#         https://zhuanlan.zhihu.com/p/62031783
#         https://wiki.mbalib.com/wiki/二项期权定价模型
#     '''
#     # 一.生成二叉树
#     dt = T / M  # length of time interval
#     df = exp(-r * dt)  # discount per interval
#     inf = exp(r * dt)  # discount per interval

#     # 计算udp
#     u = exp(sigma * sqrt(dt))  # up movement
#     d = 1 / u  # down movement
#     q = (exp(r * dt) - d) / (u - d)  # martingale branch probability

#     # 初始化幂矩阵
#     mu = np.arange(M + 1)
#     mu = np.resize(mu, (M + 1, M + 1))
#     md = np.transpose(mu)

#     # 计算个节点单向变动时的股票价格
#     mus = u ** (mu - md)
#     mds = d ** md

#     # 得到各节点的股票价格
#     S = Pnow * mus * mds

#     # 二.计算每个节点股票的预期价格
#     mes = Pnow * inf ** mu

#     # 三.得到叶子结点的期权价值
#     if otype == 'call':
#         V = np.maximum(S - K, 0)
#         #计算每个节点提前行权的收益
#         oreturn = mes - K
#     else:
#         V = np.maximum(K - S, 0)
#         #计算每个节点提前行权的收益
#         oreturn = K - mes

#     # 四.逐步向前加权平均折现和提前行权的收益比较，得到期初期权价值
#     for z in range(0, M):  # backwards iteration
#         #计算后期折现的后期价格
#         ovalue = (q * V[0:M - z, M - z] +
#                           (1 - q) * V[1:M - z + 1, M - z]) * df
#         #逐列更新期权价值，相当于二叉树中的逐层向前折算
#         #期权价格取后期折现和提前行权获得收益的最大值
#         V[0:M - z, M - z - 1] = np.maximum(ovalue, oreturn[0:M - z, M - z - 1])
#         # 原文评论区纠错代码
          # V[0:M - z, M - z - 1] = np.maximum(ovalue, V[0:M - z, M - z - 1])

#     return V[0, 0]


def BSM_IV_dichotomy(Pnow, Pexe, Popt, D, opt_type, r=3/100, i_d=0.0,
                     D_year=365, sigma_max=3.0, sigma_min=0.0,
                     tol=1e-6, Ntol=100, max_iter=10000):
    '''
    二分法求隐含波动率

    Parameters
    ----------
    Pnow: 标的现价
    Pexe: 标的执行价
    Popt: 期权现价
    D: 剩余天数
    opt_type: 期权类型
    r: 无风险利率，年化
    i_d: 隐含分红率？
    D_year: 一年天数，默认为365，即自然天数（也可以只考虑交易天数）
    sigma_max: 隐含波动率上限
    sigma_min: 隐含波动率下限
    tol, Ntol: 迭代误差控制（当计算的理论期权价格连续Ntol次迭代改变量均不超过tol时结束）
    max_iter: 迭代最大次数控制

    Returns
    -------
    sigma_iv: 返回隐含波动率求解结果

    参考：
    https://zhuanlan.zhihu.com/p/142685333
    https://www.jianshu.com/p/e73f538859df
    '''

    sigma_top, sigma_floor = sigma_max, sigma_min
    sigma_iv = (sigma_floor + sigma_top) / 2 # 隐含波动率二分法初始值
    Popt_est, Popt_last = 0, 0 # 期权价格估计值初始化
    Cnt = 0 # 计数器
    dif, ndif, last_tol_OK = np.inf, 0, False
    while dif > tol or ndif < Ntol:
        if opt_type.lower() in call_names:
            Popt_est, _ = BS_opt(Pnow, Pexe, D, r=r, sigma=sigma_iv, i_d=i_d,
                                 D_year=D_year)
        elif opt_type.lower() in put_names:
            _, Popt_est = BS_opt(Pnow, Pexe, D, r=r, sigma=sigma_iv, i_d=i_d,
                                 D_year=D_year)

        dif = abs(Popt_last - Popt_est)
        if dif <= tol and last_tol_OK:
            ndif += 1
        if dif <= tol:
            last_tol_OK = True
        else:
            last_tol_OK = False
            ndif = 0

        Popt_last = Popt_est

        # 根据价格判断波动率是被低估还是高估，并对隐含波动率进行修正
        if Popt - Popt_est > 0:
            sigma_floor = sigma_iv
            sigma_iv = (sigma_iv + sigma_top) / 2
        elif Popt - Popt_est < 0:
            sigma_top = sigma_iv
            sigma_iv = (sigma_iv + sigma_floor) / 2
        else:
            return sigma_iv

        # 注：时间价值为0的期权是算不出隐含波动率的，因此设置检查机制，
        # 迭代到一定次数就不再继续了
        Cnt += 1
        if Cnt > max_iter:
            # sigma_iv = 0
            break

    return sigma_iv


def BSM_IV_dichotomy0(Pnow, Pexe, Popt, D, opt_type, r=3/100, i_d=0.0,
                      D_year=365, sigma_max=3.0, sigma_min=0.0,
                      tol=1e-6, max_iter=10000):
    '''
    二分法求隐含波动率

    Parameters
    ----------
    Pnow: 标的现价
    Pexe: 标的执行价
    Popt: 期权现价
    D: 剩余天数
    opt_type: 期权类型
    r: 无风险利率，年化
    i_d: 隐含分红率？
    D_year: 一年天数，默认为365，即自然天数（也可以只考虑交易天数）
    sigma_max: 隐含波动率上限
    sigma_min: 隐含波动率下限
    tol: 迭代误差控制
    max_iter: 迭代最大次数控制

    Returns
    -------
    sigma_iv: 返回隐含波动率求解结果

    参考：
    https://zhuanlan.zhihu.com/p/142685333
    https://www.jianshu.com/p/e73f538859df
    '''

    sigma_top, sigma_floor = sigma_max, sigma_min
    sigma_iv = (sigma_floor + sigma_top) / 2 # 隐含波动率二分法初始值
    Popt_est = 0 # 期权价格估计值初始化
    Cnt = 0 # 计数器
    while abs(Popt - Popt_est) > tol:
        if opt_type.lower() in call_names:
            Popt_est, _ = BS_opt(Pnow, Pexe, D, r=r, sigma=sigma_iv, i_d=i_d,
                                 D_year=D_year)
        elif opt_type.lower() in put_names:
            _, Popt_est = BS_opt(Pnow, Pexe, D, r=r, sigma=sigma_iv, i_d=i_d,
                                 D_year=D_year)

        # 根据价格判断波动率是被低估还是高估，并对隐含波动率进行修正
        if Popt - Popt_est > 0:
            sigma_floor = sigma_iv
            sigma_iv = (sigma_iv + sigma_top) / 2
        elif Popt - Popt_est < 0:
            sigma_top = sigma_iv
            sigma_iv = (sigma_iv + sigma_floor) / 2
        else:
            return sigma_iv

        # 注：时间价值为0的期权是算不出隐含波动率的，因此设置检查机制，
        # 迭代到一定次数就不再继续了
        Cnt += 1
        if Cnt > max_iter:
            return sigma_iv
            # sigma_iv = 0
            # break

    return sigma_iv


def BSM_IV_newton(Pnow, Pexe, Popt, D, opt_type, r=3/100, i_d=0.0,
                  sigma_iv_init=None, D_year=365, lr=0.1, max_iter=1000):
    '''
    牛顿法计算隐含波动率

    Parameters
    ----------
    Pnow: 标的现价
    Pexe: 标的执行价
    Popt: 期权现价
    D: 剩余天数
    opt_type: 期权类型
    r: 无风险利率，年化
    i_d: 隐含分红率？
    sigma_iv_init: 设置隐含波动率初始值
    D_year: 一年天数，默认为365，即自然天数（也可以只考虑交易天数）
    lr: 学习率
    max_iter: 迭代最大次数控制

    Returns
    -------
    sigma_iv: 返回隐含波动率求解结果

    参考：
    https://www.jianshu.com/p/e73f538859df
    '''

    if sigma_iv_init is None:
        sigma_iv_init = 1
    sigma_iv = sigma_iv_init

    k = 0
    while k < max_iter:
        if opt_type.lower() in call_names:
            Popt_est, _ = BS_opt(Pnow, Pexe, D, r=r, sigma=sigma_iv, i_d=i_d,
                                 D_year=D_year)
        elif opt_type.lower() in put_names:
            _, Popt_est = BS_opt(Pnow, Pexe, D, r=r, sigma=sigma_iv, i_d=i_d,
                                 D_year=D_year)

        vega = BS_vega(Pnow, Pexe, D, r=r, sigma=sigma_iv, i_d=i_d, D_year=D_year)

        sigma_iv -= lr * (Popt_est - Popt) / vega

        k += 1

    return sigma_iv


def BS_vega(Pnow, Pexe, D, r=3/100, sigma=25/100, i_d=0, D_year=365):
    '''
    BS公式，Vega计算

    Parameters
    ----------
    Pnow: 标的现价
    Pexe: 标的执行价
    D: 剩余天数
    r: 无风险利率，年化
    sigma: 波动率
    i_d: 隐含分红率？
    D_year: 一年天数，默认为365，即自然天数（也可以只考虑交易天数）

    Returns
    -------
    vega: 返回vega求解结果

    参考：
    https://blog.csdn.net/zita_11/article/details/104200887
    https://zhuanlan.zhihu.com/p/135867175
    '''

    T = D / D_year
    d1 = (log(Pnow / Pexe) + (r - i_d + 0.5 * sigma ** 2) * T) / (sigma * sqrt(T))

    vega = Pnow * exp(-i_d * T) * norm.pdf(d1) * sqrt(T)

    return vega


def BS_delta(Pnow, Pexe, D, opt_type, r=3/100, sigma=25/100, i_d=0.0,
             D_year=365):
    '''
    注：分红处理可能不对！
    BS公式，Delta计算

    Parameters
    ----------
    Pnow: 标的现价
    Pexe: 标的执行价
    D: 剩余天数
    opt_type: 期权类型
    r: 无风险利率，年化
    sigma: 波动率
    i_d: 隐含分红率？
    D_year: 一年天数，默认为365，即自然天数（也可以只考虑交易天数）

    Returns
    -------
    vega: 返回delta求解结果

    参考：
    https://blog.csdn.net/zita_11/article/details/104200887
    https://zhuanlan.zhihu.com/p/113915774
    '''

    T = D / D_year
    d1 = (log(Pnow / Pexe) + (r - i_d + 0.5 * sigma ** 2) * T) / (sigma * sqrt(T))

    if opt_type.lower() in call_names:
        delta = norm.cdf(d1)
    elif opt_type.lower() in put_names:
        delta = -norm.cdf(-d1)

    return delta


def BS_gamma(Pnow, Pexe, D, r=3/100, sigma=25/100, i_d=0.0, D_year=365):
    '''
    注：分红处理可能不对！
    BS公式，Delta计算

    Parameters
    ----------
    Pnow: 标的现价
    Pexe: 标的执行价
    D: 剩余天数
    r: 无风险利率，年化
    sigma: 波动率
    i_d: 隐含分红率？
    D_year: 一年天数，默认为365，即自然天数（也可以只考虑交易天数）

    Returns
    -------
    gamma: 返回gamma求解结果

    参考：
    https://blog.csdn.net/zita_11/article/details/104200887
    https://zhuanlan.zhihu.com/p/113915774
    '''

    T = D / D_year
    d1 = (log(Pnow / Pexe) + (r - i_d + 0.5 * sigma ** 2) * T) / (sigma * sqrt(T))

    gamma = norm.pdf(d1) / (Pnow * sigma * sqrt(T))

    return gamma


def BS_theta(Pnow, Pexe, D, opt_type, r=3/100, sigma=25/100, i_d=0.0,
             D_year=365):
    '''
    注：分红处理可能不对！
    BS公式，Delta计算

    Parameters
    ----------
    Pnow: 标的现价
    Pexe: 标的执行价
    D: 剩余天数
    opt_type: 期权类型
    r: 无风险利率，年化
    sigma: 波动率
    i_d: 隐含分红率？
    D_year: 一年天数，默认为365，即自然天数（也可以只考虑交易天数）

    Returns
    -------
    theta: 返回theta求解结果

    参考：
    https://blog.csdn.net/zita_11/article/details/104200887
    https://zhuanlan.zhihu.com/p/113915774
    '''

    T = D / D_year
    d1 = (log(Pnow / Pexe) + (r - i_d + 0.5 * sigma ** 2) * T) / (sigma * sqrt(T))
    d2 = d1 - sigma * sqrt(T)

    tmp1 = -1 * (Pnow * norm.pdf(d1) * sigma) / (2 * sqrt(T))
    if opt_type.lower() in call_names:
        n = 1
    elif opt_type.lower() in put_names:
        n = -1
    tmp2 = n * r * Pexe * np.exp(-r * T) * norm.cdf(n * d2)

    theta = (tmp1 - tmp2) / D_year

    return theta


def BS_rho(Pnow, Pexe, D, opt_type, r=3/100, sigma=25/100, i_d=0.0,
           D_year=365):
    '''
    注：分红处理可能不对！
    BS公式，Delta计算

    Parameters
    ----------
    Pnow: 标的现价
    Pexe: 标的执行价
    D: 剩余天数
    opt_type: 期权类型
    r: 无风险利率，年化
    sigma: 波动率
    i_d: 隐含分红率？
    D_year: 一年天数，默认为365，即自然天数（也可以只考虑交易天数）

    Returns
    -------
    rho: 返回rho求解结果

    参考：
    https://zhuanlan.zhihu.com/p/137938792
    '''

    T = D / D_year
    d1 = (log(Pnow / Pexe) + (r - i_d + 0.5 * sigma ** 2) * T) / (sigma * sqrt(T))
    d2 = d1 - sigma * sqrt(T)

    if opt_type.lower() in call_names:
        rho = T * Pexe * exp(-r * T) * norm.cdf(d2)
    elif opt_type.lower() in put_names:
        rho = -1 * T * Pexe * exp(-r * T) * norm.cdf(-d2)

    return rho


if __name__ == '__main__':
    # import warnings
    # warnings.filterwarnings('ignore')

    # BS公式&蒙特卡罗测试--------------------------------------------------------
    Pnow = 3.731
    Pexe = 3.5
    D = 100
    r = 3/100
    i_d = 0.0/100
    sigma = 25/100
    D_year = 365
    N_mc = 1000
    random_seed = None

    # BS|蒙特卡罗|BOPM计算期权理论价格
    Popt_bs = BS_opt(Pnow, Pexe, D, r=r, sigma=sigma, i_d=i_d, D_year=D_year)
    Popt_mc = MCBS_opt(Pnow, Pexe, D, r=r, sigma=sigma, D_year=D_year,
                       N_mc=N_mc, random_seed=random_seed, kwargs_plot=None)
    Popt_mc_log = MCBSlog_opt(Pnow, Pexe, D, r=r, sigma=sigma, D_year=D_year,
                              N_mc=N_mc, random_seed=random_seed,
                              kwargs_plot=None)
    Popt_bopm = BOPM_european(Pnow, Pexe, D, r=r, sigma=sigma, D_year=D_year)
    print('看涨：')
    print('Popt_bs: {}'.format(round(Popt_bs[0], 6)))
    print('Popt_mc: {}'.format(round(Popt_mc[0], 6)))
    print('Popt_mclog: {}'.format(round(Popt_mc_log[0], 6)))
    print('Popt_bopm: {}'.format(round(Popt_bopm[0], 6)))
    print('看跌：')
    print('Popt_bs: {}'.format(round(Popt_bs[1], 6)))
    print('Popt_mc: {}'.format(round(Popt_mc[1], 6)))
    print('Popt_mclog: {}'.format(round(Popt_mc_log[1], 6)))
    print('Popt_bopm: {}'.format(round(Popt_bopm[1], 6)))


    # BS公式计算隐含波动率
    # Popt = 0.0702
    # opt_type = 'p'
    Popt = 0.1071
    opt_type = 'c'

    sigma_iv = BSM_IV_dichotomy(Pnow, Pexe, Popt, D, opt_type, r=r, i_d=i_d)
    print('二分法隐波: {}'.format(round(sigma_iv, 10)))
    sigma_iv = BSM_IV_newton(Pnow, Pexe, Popt, D, opt_type, r=r, i_d=i_d)
    print('牛顿法隐波: {}'.format(round(sigma_iv, 10)))


    # BS-vega
    vega = BS_vega(Pnow, Pexe, D, r=r, sigma=sigma, i_d=i_d, D_year=D_year)
    print('BS-vega: {}'.format(round(vega, 6)))


    # BS-delta
    delta = BS_delta(Pnow, Pexe, D, opt_type, r=r, sigma=sigma, i_d=i_d,
                     D_year=D_year)
    print('BS-delta: {}'.format(round(delta, 6)))


    # BS-gamma
    gamma = BS_gamma(Pnow, Pexe, D, r=r, sigma=sigma, i_d=i_d, D_year=D_year)
    print('BS-gamma: {}'.format(round(gamma, 6)))


    # BS-theta
    theta = BS_theta(Pnow, Pexe, D, opt_type, r=r, sigma=sigma, i_d=i_d,
                     D_year=D_year)
    print('BS-theta: {}'.format(round(theta, 6)))


    # BS-rho
    rho = BS_rho(Pnow, Pexe, D, opt_type, r=r, sigma=sigma, i_d=i_d,
                 D_year=D_year)
    print('BS-rho: {}'.format(round(rho, 6)))
