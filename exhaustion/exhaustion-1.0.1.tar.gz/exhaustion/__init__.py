from inspect import signature

from typing import Any, Callable


def booleanize(bit_string: str, length: int):
    """ Converts the given bit string to a list of Booleans, padding with False to the left to the given length.

    Args:
        bit_string (str): The bit string to convert.
        length (int): The length to which to pad the resulting array of Booleans with False to the left.
    Returns:
        list of bool: The resulting list of Booleans.
    """
    booleanized = [char == '1' for char in bit_string] # From bit string to list of Booleans.
    while len(booleanized) < length:
        booleanized.insert(0, False) # Pad with False to the left.
    return booleanized


def permute(arity: int):
    """ Returns every permutation of Boolean arguments to a function with the given arity.

    Args:
        arity (int): The arity of the function to get every permutation of Boolean arguments for.
    Returns:
        list of list of bool: The resulting list of arguments lists.
    """
    # Use ascending numbers converted to binary for permutations.
    return [booleanize('{0:b}'.format(i), arity) for i in range(0, 2**arity)]


def exhaust(func: Callable[..., Any]):
    """ Calls a function taking only Boolean parameters with every permutation of parameters possible.

    Args:
        func (Callable[..., Any]): The function to call.
    """
    arg_permutations = permute(len(signature(func).parameters))
    for arg_permutation in arg_permutations:
        func(*arg_permutation)
