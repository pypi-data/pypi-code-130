"""This module provides functions to work with nested dictionaries

"""

from typing import Tuple, Iterable

from formgram.grammars.helper_functions.decorators import deepcopy_arguments


@deepcopy_arguments
def insert_to_nested_dict(nested_dict: dict, insert: tuple) -> dict:
    """This function creates a new nested dictionary, with a new insertion

   :example:
        >>> d = {"a": {"b": {"c": {1}}}
        >>> insert_to_nested_dict(d, ("a","b","d",{1,2,3}))
        {"a": {"b": {"c": {1}, "d": {1,2,3}}}

    :param nested_dict:
    :param insert: subscribable Iterable
    :return: a new dict with the tuple inserted in a nested manner
    """
    i = 0
    current = nested_dict
    try:
        for i, element in enumerate(insert[:-1]):
            current = current[element]
        current.add(insert[-1])
    except KeyError:
        structure = {insert[-1]}  # create the core as a set with single entry
        for element in list(insert)[i + 1: -1][::-1]:  # nest dicts around the core
            structure = {element: structure}
        current[insert[i]] = structure
    return nested_dict


def create_nested_dict(edges: Iterable[Tuple[str, ...]]) -> dict:
    """Create a nested dictionary from a set

    :example:
        >>> edge_set = [("A", "a", "A"),
        >>>     ("A", None, "B"),
        >>>     ("A", "a", "C"),
        >>>     ("B", "b", "B"),]
        >>> create_nested_dict(edge_set)
        {
            "A" : {
                "a" : {"A", "C"},
                None : {"B", },
            },
            "B" : {
                "b" : {"B", },
        }

    :param edges:
    :return: A new nested dict representation of the given tuples
    """
    new_nested_dict = {}
    for data_tuple in edges:
        new_nested_dict = insert_to_nested_dict(new_nested_dict, data_tuple)
    return new_nested_dict
