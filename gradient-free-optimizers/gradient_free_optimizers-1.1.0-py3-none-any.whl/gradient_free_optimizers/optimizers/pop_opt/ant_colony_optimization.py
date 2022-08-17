# Author: Simon Blanke
# Email: simon.blanke@yahoo.com
# License: MIT License


import numpy as np

from .base_population_optimizer import BasePopulationOptimizer
from ...search import Search


class AntColonyOptimization(BasePopulationOptimizer, Search):
    name = "Ant Colony Optimization"
    _name_ = "ant_colony_optimization"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def iterate(self):
        pass
