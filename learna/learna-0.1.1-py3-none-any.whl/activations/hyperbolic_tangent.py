# Tanh is another nonlinear activation function.
# Tanh outputs between -1 and 1.
# Tanh also suffers from gradient problem near the boundaries
# just as Sigmoid activation function does.
import numpy as np


def hyperbolic_tangent(x):
    return np.tanh(x)
