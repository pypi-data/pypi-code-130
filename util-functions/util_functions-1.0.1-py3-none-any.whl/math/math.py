import numpy as np


__all__ = ["gini_coefficient", "is_numeric"]


def gini_coefficient(collection, precision: int = None):
    """
    This function calculates Gini coefficient (index) for a list, series, array or an analogous
    collections of numbers.

    Args:
        collection (Union[List, Tuple, np.array, pd.Series]): collection of numbers
        precision (int): number of digits after decimal separator which are to be returned

    Returns:
        (float): value of Gini coefficient

    Examples:
        >>> gini_coefficient([1, 3, 5])
        0.2962962962962963

        >>> gini_coefficient([1, 3, 5], 3)
        0.296
    """
    collection = list(collection)

    if not (isinstance(collection, list) and all([is_numeric(item) for item in collection])):
        raise TypeError("Parameter 'collection' should be a list of numeric values")

    if precision is not None and not isinstance(precision, int):
        raise TypeError("Parameter 'precision' should be an integer")

    mean_absolute_difference = np.abs(np.subtract.outer(collection, collection)).mean()
    relative_mean_absolute_difference = mean_absolute_difference / np.mean(collection)
    gini = 0.5 * relative_mean_absolute_difference
    if precision is not None:
        gini = round(gini, precision)

    return gini


def is_numeric(x):
    """
    This function checks if the input value is a numerical value such as: int, float, np.int, ...

    Args:
        x: any object

    Returns:
        (bool): whether the object is a numeric type

    Examples:
         >>> is_numeric(2.1)
         True

         >>> is_numeric("abc")
         False
    """
    if isinstance(x, (int, float, np.integer, np.float)):
        return True
    else:
        return False
