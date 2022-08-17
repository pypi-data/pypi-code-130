# Author: Simon Blanke
# Email: simon.blanke@yahoo.com
# License: MIT License


import numpy as np
from numpy.random import normal
from scipy.spatial.distance import cdist

from ..local_opt import HillClimbingOptimizer


class Ant(HillClimbingOptimizer):
    def __init__(self, *args, alpha=1, beta=1, rho=0.5, **kwargs):
        super().__init__(*args, **kwargs)
        self.alpha = alpha
        self.beta = beta
        self.rho = rho

    def local_positions(self, n_positions=10):
        positions_l = []
        sigma = self.conv.max_positions * self.epsilon
        pos_c = self.pos_current

        for _ in range(n_positions):

            pos_normal = normal(pos_c, sigma, pos_c.shape)

            positions_l.append(pos_normal)

        return positions_l

    def p_move(self, position):
        positions_l = self.local_positions()

        denominator = 0
        for pos_local in positions_l:

            pos_dist = cdist(pos_local, position)

            denominator += 1 / pos_dist
