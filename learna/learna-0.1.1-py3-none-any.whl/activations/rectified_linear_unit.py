# RELU is more well known activation function which is used in the
# deep learning networks. RELU is less computational expensive than
# the other non linear activation functions.
#   RELU returns 0 if the x (input) is less than 0
#   RELU returns x if the x (input) is greater than 0
import numpy as np


def rectified_linear_unit(x):
    return np.maximum(0, x)
