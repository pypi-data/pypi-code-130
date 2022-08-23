# -*- coding: utf-8 -*-

import time
import pandas as pd
from utils_hoo.utils_optimizer.GA import GA
from utils_hoo.utils_optimizer.CS import CS
from utils_hoo.utils_optimizer.PSO import PSO
from utils_hoo.utils_optimizer.GWO import GWO
from utils_hoo.utils_optimizer.WOA import WOA
from utils_hoo.utils_optimizer.HHO import HHO
from utils_hoo.utils_optimizer.ALO import ALO
from utils_hoo.utils_optimizer.BOA import BOA
from utils_hoo.utils_optimizer.HPSOBOA import HPSOBOA
from utils_hoo.utils_optimizer.HCPSOBOA import HCPSOBOA
from utils_hoo.utils_general import simple_logger
from utils_hoo.utils_plot.plot_Common import plot_Series
from utils_hoo.utils_optimizer.test_funcs import TestFuncs
from utils_hoo.utils_logging.logger_general import get_logger
from utils_hoo.utils_logging.logger_utils import close_log_file
from utils_hoo.utils_optimizer.utils_Heuristic import FuncOpterInfo


if __name__ == '__main__':
    strt_tm = time.time()

    # 目标函数和参数
    objf = TestFuncs.F1
    parms_func = {'func_name': objf.__name__,
                  'x_lb': -10, 'x_ub': 10, 'dim': 100, 'kwargs': {}}

    # 统一参数
    PopSize = 30
    Niter = 500

    # logger
    # logger = simple_logger()
    logger = get_logger('./test/Heuristic-test.txt', screen_show=True)
    # parms_log = {'logger': logger, 'nshow': 10}
    parms_log = {'logger': logger, 'nshow': Niter}

    fvals = pd.DataFrame()

    # GA
    parms_ga = {'opter_name': 'GA',
                'PopSize': PopSize, 'Niter': Niter,
                'Pcrs': 0.7, 'Pmut': 0.1, 'Ntop': 2}

    ga_parms = FuncOpterInfo(parms_func, parms_ga, parms_log)
    ga_parms = GA(objf, ga_parms)
    fvals['GA'] = ga_parms.convergence_curve

    # PSO
    parms_pso = {'opter_name': 'PSO',
                 'PopSize': PopSize, 'Niter': Niter,
                 'v_maxs': 5, 'w_max': 0.9, 'w_min': 0.2, 'w_fix': False,
                 'c1': 2, 'c2': 2}

    pso_parms = FuncOpterInfo(parms_func, parms_pso, parms_log)
    pso_parms = PSO(objf, pso_parms)
    fvals['PSO'] = pso_parms.convergence_curve

    # CS
    parms_cs = {'opter_name': 'CS',
                'PopSize': PopSize, 'Niter': Niter,
                'pa': 0.25, 'beta': 1.5, 'alpha': 0.01}

    cs_parms = FuncOpterInfo(parms_func, parms_cs, parms_log)
    cs_parms = CS(objf, cs_parms)
    fvals['CS'] = cs_parms.convergence_curve

    # GWO
    parms_gwo = {'opter_name': 'GWO',
                 'PopSize': PopSize, 'Niter': Niter}

    gwo_parms = FuncOpterInfo(parms_func, parms_gwo, parms_log)
    gwo_parms = GWO(objf, gwo_parms)
    fvals['GWO'] = gwo_parms.convergence_curve

    # WOA
    parms_woa = {'opter_name': 'WOA',
                 'PopSize': PopSize, 'Niter': Niter}

    woa_parms = FuncOpterInfo(parms_func, parms_woa, parms_log)
    woa_parms = WOA(objf, woa_parms)
    fvals['WOA'] = woa_parms.convergence_curve

    # HHO
    parms_hho = {'opter_name': 'HHO',
                 'PopSize': PopSize, 'Niter': Niter,
                 'beta': 1.5, 'alpha': 0.01}

    hho_parms = FuncOpterInfo(parms_func, parms_hho, parms_log)
    hho_parms = HHO(objf, hho_parms)
    fvals['HHO'] = hho_parms.convergence_curve

    # BOA
    parms_boa = {'opter_name': 'BOA',
                 'PopSize': PopSize, 'Niter': Niter,
                 'p': 0.6, 'power_exponent': 0.1, 'sensory_modality': 0.01}

    boa_parms = FuncOpterInfo(parms_func, parms_boa, parms_log)
    boa_parms = BOA(objf, boa_parms)
    fvals['BOA'] = boa_parms.convergence_curve

    # HPSOBOA
    parms_hpsoboa = {'opter_name': 'HPSOBOA',
                     'PopSize': PopSize, 'Niter': Niter,
                     'p': 0.6, 'power_exponent': 0.1, 'sensory_modality': 0.01}

    hpsoboa_parms = FuncOpterInfo(parms_func, parms_hpsoboa, parms_log)
    hpsoboa_parms = HPSOBOA(objf, hpsoboa_parms)
    fvals['HPSOBOA'] = hpsoboa_parms.convergence_curve

    # HCPSOBOA
    parms_hcpsoboa = {'opter_name': 'HCPSOBOA',
                      'PopSize': PopSize, 'Niter': Niter,
                      'p': 0.6, 'power_exponent': 0.1,
                      'sensory_modality': 0.01}

    hcpsoboa_parms = FuncOpterInfo(parms_func, parms_hcpsoboa, parms_log)
    hcpsoboa_parms = HCPSOBOA(objf, hcpsoboa_parms)
    fvals['HCPSOBOA'] = hcpsoboa_parms.convergence_curve

    # # ALO
    # parms_alo = {'opter_name': 'ALO',
    #              'PopSize': PopSize, 'Niter': Niter}

    # alo_parms = FuncOpterInfo(parms_func, parms_alo, parms_log)
    # alo_parms = ALO(objf, alo_parms)
    # fvals['ALO'] = alo_parms.convergence_curve


    # 参数汇总
    Results = pd.DataFrame({'ga': ga_parms.best_x,
                            'pso': pso_parms.best_x,
                            'cs': cs_parms.best_x,
                            'gwo': gwo_parms.best_x,
                            'woa': woa_parms.best_x,
                            'hho': hho_parms.best_x,
                            'boa': boa_parms.best_x,
                            'hpsoboa': hpsoboa_parms.best_x,
                            'hcpsoboa': hcpsoboa_parms.best_x,
                            # 'alo': alo_parms.best_x
                            })


    # 作图比较
    plot_Series(fvals.iloc[150:, :],
                {'GA': '-', 'PSO': '-', 'CS': '-', 'GWO': '-', 'WOA': '-',
                 'HHO': '-', 'BOA': '-', 'HPSOBOA': '-', 'HCPSOBOA': '-',
                 # 'ALO': '-'
                 },
                figsize=(10, 6))


    close_log_file(logger)


    print('used time: {}s.'.format(round(time.time()-strt_tm, 6)))
