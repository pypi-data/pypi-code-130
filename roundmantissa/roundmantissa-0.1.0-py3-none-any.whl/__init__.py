import math

__version__ = "0.1.0"


def round_mantissa(x: float, n: int) -> float:
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
    if x == 0:
        return 0
    s = 1 if x >= 0 else -1
    x = abs(x)
    a = math.floor(math.log2(x))
    x = x / 2**a
    assert 1.0 <= x < 2.0, x
    x = round(x * 2**n) / 2**n
    x = x * 2**a
    return s * x
