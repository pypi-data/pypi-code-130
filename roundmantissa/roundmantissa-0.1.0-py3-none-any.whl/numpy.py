import numpy as np


def round_mantissa(x: np.ndarray, n: int) -> np.ndarray:
    """Round number

    Args:
        x: number to round
        n: number of mantissa digits to keep

    Returns:
        rounded number

    Example:
        >>> round_mantissa(0.5 + 0.25 + 0.125, 0)
        1.0

        >>> round_mantissa(0.5 + 0.25 + 0.125, 2)
        0.875
    """

    def fn(x):
        s = np.sign(x)
        x = np.abs(x)
        a = np.floor(np.log2(x))
        x = x / 2**a
        assert np.all(1.0 <= x) and np.all(x < 2.0), x
        x = np.round(x * 2**n) / 2**n
        x = x * 2**a
        return s * x

    return np.where(x == 0.0, 0.0, fn(np.where(x == 0.0, 1.0, x)))
