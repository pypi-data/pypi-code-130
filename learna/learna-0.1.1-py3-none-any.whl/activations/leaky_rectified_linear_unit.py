import numpy as np


def leaky_rectified_linear_unit(x):
    # This approach maybe a bit faster
    # y1 = ((x > 0) * x)
    # y2 = ((x <= 0) * x * 0.01)
    # return y1 + y2

    return np.where(x > 0, x, x * 0.01)
