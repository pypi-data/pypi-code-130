# Binary step function returns value either 0 or 1.
# It returns '0' if the input is the less then zero
# It returns '1' if the input is greater than zero
import numpy as np


def binary_step(x):
    """It returns '0' is the input is less then zero
    otherwise it returns one"""
    return np.heaviside(x, 1)
