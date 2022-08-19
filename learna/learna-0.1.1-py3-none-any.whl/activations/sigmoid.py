# Sigmoid function returns the value beteen 0 and 1.
# For activation function in deep learning network,
# Sigmoid function is considered not good since near
# the boundaries the network doesn't learn quickly.
# This is because gradient is almost zero near the boundaries.
import numpy as np


def sigmoid(x):
    return 1 / (1 + np.exp(-x))
