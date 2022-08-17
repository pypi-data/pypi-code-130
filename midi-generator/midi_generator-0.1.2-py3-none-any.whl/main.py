import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns

from .config import Configuration
from .genetic import ea_simple_with_elitism, generator, fitness, mutation, check_remaining_ticks, individual_to_melody
from deap import base, creator, tools

from utils.output import write_file
