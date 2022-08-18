"""This module provides interfaces to graphviz and jove

"""
from types import Union

import graphviz

from formgram.grammars.helper_functions.decorators import deepcopy_arguments
from formgram.grammars.helper_functions.set_functions import find_new_unique_string


@deepcopy_arguments
def to_jove(machine: dict) -> dict:
    """

    :param machine:
    :return:
    """
    epsilon = ""
    if epsilon in machine["alphabet"]:
        raise ValueError("The empty string is needed by jove as epsilon, and can not be in the alphabet")

    jove_delta = {}
    for node, symbol, target_node in machine["transitions"]:
        if symbol is None:
            symbol = epsilon  # jove handles epsilon in a different way than grammars
        key = (node, symbol)
        if key in jove_delta:
            jove_delta[key].add(target_node)
        else:
            jove_delta[key] = {target_node}

    return {
        "Q": machine["states"],
        "Sigma": machine["alphabet"],
        "Q0": machine["starting_states"],
        "Delta": jove_delta,
        "F": machine["accepting_states"]
    }


@deepcopy_arguments
def to_dot(machine: dict, as_object: bool = False) -> Union[graphviz.Digraph, str]:
    """

    :param as_object:
    :param machine:
    :return:
    """
    graph = graphviz.Digraph()
    pre_start_node_name = find_new_unique_string(previous_symbols=machine["alphabet"] | machine["control_symbols"],
                                                 string_base="pre_start")
    graph.node(pre_start_node_name, shape="point")

    for accepting_node in machine["accepting_states"]:
        graph.node(accepting_node, shape="double_circle")
    for normal_node in machine["states"] - machine["accepting_states"]:
        graph.node(normal_node, shape="circle")
    for source, symbol, target in machine["transitions"]:
        graph.edge(source, target, label="symbol")

    if as_object:
        return graph
    else:
        return graph.source
