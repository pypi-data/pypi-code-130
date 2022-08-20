"""This module provides functions which work on :class:`Collections`
"""

import itertools
from typing import Collection, Iterable

from formgram.grammars.types import Symbol


def powerset(collection: Collection) -> Iterable:
    """This function returns an iterable powerset of the provided Collection

    Itertools are used for this as that package is quite optimized. It is a bit
    worse on very small collections but a lot faster for big collections compared
    to the naive for loop implementation

    :param collection: The Collection to return the powerset of
    :return: An itertools.chain object of the powerset of the provided Collection

    :examples:
        >>> list(powerset([1,2,3]))
        [(), (1,), (2,), (3,), (1, 2), (1, 3), (2, 3), (1, 2, 3)]

    """
    return itertools.chain.from_iterable(
        itertools.combinations(collection, length)
        for length in range(len(collection) + 1)
    )


def find_new_unique_string(previous_symbols: Collection[Symbol], string_base: Symbol) -> Symbol:
    """Create a new string not in `previous_symbols` by adding numerals

    :rtype: object
    :param previous_symbols:
    :param string_base:
    :return: a new string not in the collection of previous symbols
    """
    if string_base not in previous_symbols:
        return string_base
    i = 2
    while f"{string_base}_{i}" in previous_symbols:
        i += 1
    return f"{string_base}_{i}"
