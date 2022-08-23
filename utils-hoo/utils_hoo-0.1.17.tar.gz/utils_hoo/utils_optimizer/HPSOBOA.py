# -*- coding: utf-8 -*-

import time
import numpy as np
from utils_hoo.utils_optimizer.utils_Heuristic import rand_init
from utils_hoo.utils_general import isnull, power


def HPSOBOA(objf, func_opter_parms):
    '''
    todo:
        添加文中的cubic map随机初始化方法
        目前仅考虑自变量连续实数情况，后面可增加自变量为离散的情况

    粒子群蝴蝶混合优化算法(HPSOBOA.pdf)

    Parameters
    ----------
    objf: 目标函数，须事先转化为求极小值问题
    func_opter_parms: utils_optimizer.utils_Heuristic.FuncOpterInfo类，
        须设置parms_func、parms_opter、parms_log
    parms_func: 目标函数参数信息dict，key须包含
        x_lb: 自变量每个维度取值下界，list或数值，为list时长度应等于dim
        x_ub: 自变量每个维度取值上界，list或数值，为list时长度应等于dim
        dim: 自变量维度数

        kwargs: 目标函数接收的其它参数
    parms_opter: 优化函数参数信息dict，key须包含
        PopSize: 群体数量（每轮迭代的样本数量）
        Niter: 最大迭代寻优次数

        p: 全局/局部搜索转化概率
        power_exponent: `a` in HPSOBOA.pdf-Eq.(1)
        sensory_modality: `c` in HPSOBOA.pdf-Eq.(1)
    parms_log: 日志参数信息dict，key须包含
        logger: 日志记录器
        nshow: 若为整数，则每隔nshow轮日志输出当前最优目标函数值

    Returns
    -------
    更新优化过程之后的func_opter_parms

    参考：
    HPSOBOA.pdf
    '''

    # 参数提取
    opter_name = func_opter_parms.parms_opter['opter_name']
    if opter_name == '' or isnull(opter_name):
        opter_name  = 'HPSOBOA'
    func_opter_parms.parms_opter['opter_name'] = opter_name
    # 目标函数参数
    x_lb = func_opter_parms.parms_func['x_lb']
    x_ub = func_opter_parms.parms_func['x_ub']
    dim = func_opter_parms.parms_func['dim']
    kwargs = func_opter_parms.parms_func['kwargs']
    # 优化器参数
    PopSize = func_opter_parms.parms_opter['PopSize']
    Niter = func_opter_parms.parms_opter['Niter']
    p = func_opter_parms.parms_opter['p']
    power_exponent = func_opter_parms.parms_opter['power_exponent']
    sensory_modality = func_opter_parms.parms_opter['power_exponent']
    # 日志参数
    logger = func_opter_parms.parms_log['logger']
    nshow = func_opter_parms.parms_log['nshow']

    # 时间记录
    strt_tm = time.time()
    func_opter_parms.set_startTime(time.strftime('%Y-%m-%d %H:%M:%S'))


    # 边界统一为列表
    if not isinstance(x_lb, list):
        x_lb = [x_lb] * dim
    if not isinstance(x_ub, list):
        x_ub = [x_ub] * dim


    # 初始化所有个体|样本
    Xall = rand_init(PopSize, dim, x_lb, x_ub)

    # 保存收敛过程
    convergence_curve = np.zeros(Niter) # 全局最优值
    convergence_curve_mean = np.zeros(Niter) # 平均值

    # PSO
    velocity = 0.3 * np.random.randn(PopSize, dim) # PSO速度
    # w = 0.5 + np.random.rand() / 2
    w = 0.7

    # 初始函数值
    fvals = np.zeros(PopSize)
    for k in range(PopSize):
        fvals[k] = objf(Xall[k, :], **kwargs)
    best_idx = fvals.argmin()
    best_y = fvals[best_idx]
    best_x = Xall[best_idx]

    S = Xall.copy()


    def sensory_modality_new(x, Ngen):
        y = x + (0.025 / (x*Ngen))
        return y


    # 迭代寻优
    for t in range(1, Niter+1):
        fvals_mean = 0 # 记录每代目标函数均值
        for i in range(1, PopSize+1):
            fval = objf(S[i-1, :], **kwargs)

            # HPSOBOA.pdf-Eq.(10)，Change a by Non-linear control strategy
            mu = 2
            a = power_exponent + 0.2 * np.sin((i/PopSize)**2 / mu * np.pi)
            FP = sensory_modality * power(fval, a)

            # 全局|局部搜索
            r1, r2 = np.random.rand(), np.random.rand()
            if np.random.rand() < p: # 在最优解附件搜索
                # HPSOBOA.pdf-Eq.(13)
                # dis = r1 * r1 * best_x - w * Xall[i-1, :]
                dis = r1 * r2 * best_x - w * Xall[i-1, :]
                S[i-1, :] = w * Xall[i-1, :] + dis * FP
            else: # 在临近位置搜索
                # HPSOBOA.pdf-Eq.(14)
                JK = np.random.permutation(PopSize)
                dis = r1 * r1 * Xall[JK[0], :] - w * Xall[JK[1], :]
                # dis = r1 * r2 * Xall[JK[0], :] - w * Xall[JK[1], :]
                S[i-1, :] = w * Xall[i-1, :] + dis * FP

            # PSO速度更新，HPSOBOA.pdf-Eq.(11)
            r1, r2 = np.random.rand(), np.random.rand()
            C1, C2 = 0.5, 0.5
            velocity[i-1, :] = w*velocity[i-1, :] + \
                           C1*r1*(best_x-S[i-1, :]) + C2*r2*(best_x-S[i-1, :])

            # 越界处理
            S[i-1, :] = np.clip(S[i-1, :], x_lb, x_ub)

            # # 随机搜索
            # if np.random.rand() > 0.80:
            #     k = np.random.randint(dim)
            #     S[i-1, k] = x_lb[k] + (x_ub[k] - x_lb[k]) * np.random.rand()


            # 最优值和最优解更新
            fval = objf(S[i-1, :], **kwargs)
            if fval <= best_y:
                best_x = S[i-1, :].copy()
                best_y = fval

            if fval <= fvals[i-1]:
                Xall[i-1, :] = S[i-1, :].copy()
                fvals[i-1] = fval

                # HPSOBOA.pdf-Eq.(12)
                S[i-1, :] = S[i-1, :] + velocity[i-1, :] # PSO更新
                S[i-1, :] = np.clip(S[i-1, :], x_lb, x_ub) # 越界处理

            fvals_mean = (fvals_mean*(i-1) + fval) / i

        # Update sensory_modality
        sensory_modality = sensory_modality_new(sensory_modality, Niter)
        # power_exponent = power_exponent * np.random.rand()

        # 每轮迭代都保存最优目标值
        convergence_curve[t-1] = best_y
        convergence_curve_mean[t-1] = fvals_mean

        if nshow:
            if t % nshow ==0:
                opter_name = func_opter_parms.parms_opter['opter_name']
                func_name = func_opter_parms.parms_func['func_name']
                logger.info('{} for {}, iter: {}, '.format(opter_name, func_name, t) + \
                            'best fval: {}'.format(best_y))


    # 更新func_opter_parms
    end_tm = time.time()
    func_opter_parms.set_endTime(time.strftime('%Y-%m-%d %H:%M:%S'))
    func_opter_parms.set_exeTime(end_tm-strt_tm)
    func_opter_parms.set_convergence_curve(convergence_curve)
    func_opter_parms.set_convergence_curve_mean(convergence_curve_mean)
    func_opter_parms.set_best_val(best_y)
    func_opter_parms.set_best_x(best_x)

    return func_opter_parms


if __name__ == '__main__':
    import pandas as pd
    from utils_hoo.utils_optimizer.test_funcs import TestFuncs
    from utils_hoo.utils_optimizer.utils_Heuristic import FuncOpterInfo
    from utils_hoo.utils_plot.plot_Common import plot_Series
    from utils_hoo.utils_general import simple_logger
    from utils_hoo.utils_logging.logger_general import get_logger
    from utils_hoo.utils_logging.logger_utils import close_log_file


    strt_tm = time.time()

    objf = TestFuncs.Ackley2
    parms_func = {'func_name': objf.__name__,
                  'x_lb': -10, 'x_ub': 10, 'dim': 10, 'kwargs': {}}
    parms_opter = {'opter_name': 'HPSOBOA-test',
                   'PopSize': 30, 'Niter': 500,
                   'p': 0.6, 'power_exponent': 0.1, 'sensory_modality': 0.01}
    # logger = simple_logger()
    logger = get_logger('./test/HPSOBOA_test.txt', screen_show=True)
    # parms_log = {'logger': logger, 'nshow': 10}
    parms_log = {'logger': logger, 'nshow': 100}

    func_opter_parms = FuncOpterInfo(parms_func, parms_opter, parms_log)
    func_opter_parms = HPSOBOA(objf, func_opter_parms)

    vals = pd.DataFrame({'fval_best': func_opter_parms.convergence_curve,
                         'fval_mean': func_opter_parms.convergence_curve_mean})
    plot_Series(vals, {'fval_best': '-r', 'fval_mean': '-b'}, figsize=(10, 6))

    best_x = func_opter_parms.best_x
    func_opter_parms.parms_log['logger'].info('best x: {}'.format(best_x))

    close_log_file(logger)


    print('used time: {}s.'.format(round(time.time()-strt_tm, 6)))
