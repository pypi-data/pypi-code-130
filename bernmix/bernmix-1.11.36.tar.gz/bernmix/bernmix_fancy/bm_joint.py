"""
This module aims to
"""

import numpy as np
from bm_dynam import *
from bernmix.bernmix_int import pmf as bmi

def bm_joint(p, w_vec, v = None, tol = 1e-5):
    """
    Function to predict joint distribution of
    :param p: pribabilities of Bernoulli RVs
    :param w_vec: vector of vectors of weights for RVs
    :param tol: tolerance
    :return:
    """
    # Checks
    # TODO

    # -----------------------------------
    # Preparation
    # -----------------------------------

    # Algorithm


    w_max = [sum(w) + 1 for w in w_vec]
    m_max = np.cumprod(w_max)

    w_new = w_vec[0]
    for i in range(1, len(w_vec)):
        w_new = [w1 + w2 * m_max[i-1] for w1, w2 in zip(w_new, w_vec[i])]

    if v is None:
        s = bmi(p, w_new)
    else:
        s = dyn_tree_cov(p, w_new, v)

    res = [[i, val] for i, val in enumerate(s) if val > tol]
    prob_sum = sum([val for _, val in res])
    res = [[i, val / prob_sum] for i, val in res]

    i = 7598


    res_brv = []
    for i, val in res:
        y = []
        for j in range(len(w_max)):
            y_tmp = i % w_max[j]
            y += [y_tmp]
            i -= y_tmp
            i /= w_max[j]
            i = round(i)
        res_brv += [y + [val]]




