import numpy as np


def sphere(x):
    """Sphere function.

    .. math::

       f(\\mathbf{x}) = \\sum_{i=1}^n x_i^2

    Parameters
    ----------
    x : array_like
        A real-valued vector to evaluate.

    Returns
    -------
    float
        Function value at x.

    References
    ----------
    .. [1] "Test functions for optimization", Wikipedia,
           `<https://en.wikipedia.org/wiki/Test_functions_for_optimization>`_

    Examples
    --------
    >>> sphere([0, 0])
    0.0
    >>> sphere([1, 1])
    2.0
    """
    return float((np.asarray(x) ** 2).sum())
