"""This module provides functions to classify finite automata

"""

from formgram.machines.helper_functions.nested_dictionaries import create_nested_dict


def has_epsilon_transitions(machine: dict) -> bool:
    """Determine if the machine has any epsilon transitions

    :param machine:
    :return: True if at least one epsilon transition is in the machine
    """
    return len(find_epsilon_edges(machine["edges"])) > 0


def has_alternate_symbol_choices(machine: dict) -> bool:
    """Determine if there is a node which two edges with the same symbol pointing to different nodes

    :param machine:
    :return: True if there is at least one node with two transitions using the same symbol
    """
    edges = machine["edges"]
    nested_edge_dict = create_nested_dict(edges)
    for source in nested_edge_dict:
        for symbol in nested_edge_dict[source]:
            if len(nested_edge_dict[source][symbol]) > 1:
                return False
    return True


def is_total(machine: dict) -> bool:
    """Determine if a machine is total, meaning that is has

    :param machine:
    :return: True if each node has a transition for each symbol
    """
    edge_dict = create_nested_dict(machine["edges"])
    if not machine["nodes"].issuperset(edge_dict):
        return False  # There are nodes without edges
    for source in edge_dict:
        if not machine["alphabet"].issuperset(edge_dict[source]):
            return False  # this node fails to have some of the alphabet edges
    return True


def has_single_starting_node(machine: dict) -> bool:
    """Determine if the set of starting nodes contains exactly one node

    :param machine:
    :return: True if there is only one starting node
    """
    return len(machine["starting_nodes"]) == 1


def validate_correctness(machine: dict) -> None:
    """Validate that all assumed qualities of a finite machine are fulfilled

    This means that the keys

    * starting_nodes
    * accepting_nodes
    * nodes
    * alphabet
    * edges

    are all in the dictionary

    :param machine:
    """
    required_keys = {"edges", "alphabet", "nodes", "starting_nodes", "accepting_nodes"}
    if not required_keys.issuperset(machine):
        raise KeyError(f"Missing keys: {required_keys.difference(machine)}")
    if not machine["nodes"].issuperset(machine["starting_nodes"]):
        raise KeyError(
            f"starting nodes not included in nodes set: {machine['starting_nodes'].difference(machine['nodes'])}"
        )
    if not machine["nodes"].issuperset(machine["starting_nodes"]):
        raise KeyError(
            f"accepting nodes not included in nodes set: {machine['accepting_nodes'].difference(machine['nodes'])}"
        )
    alphabet_errors = [
        (source, symbol, target)
        for (source, symbol, target) in machine["edges"]
        if symbol not in machine["alphabet"]
    ]
    if alphabet_errors:
        raise ValueError(
            f"following edges use symbols not included in the alphabet: {alphabet_errors}"
        )

    node_errors = [
        (source, symbol, target)
        for (source, symbol, target) in machine["edges"]
        if {source, target}.difference(machine["alphabet"])
    ]
    if node_errors:
        raise ValueError(
            f"following edges use nodes not included in the nodes set: {node_errors}"
        )


def is_deterministic(machine: dict) -> bool:
    """Determine if the finite automaton is a deterministic one

    :param machine:
    :return: True if the machine has no choice how to transition from a node
    """
    return (
        not has_epsilon_transitions(machine)
        and has_single_starting_node(machine)
        and not has_alternate_symbol_choices(machine)
    )


def find_epsilon_edges(edges: set) -> set:
    """Determine all edges which have None as transition symbol

    :param edges: A set of edge tuples
    :return: A set of edge tuples with None as transition symbol
    """
    epsilon_edges = set()
    for edge in edges:
        source_node, transition_symbol, target_node = edge
        if transition_symbol is None:
            epsilon_edges.add(edge)
    return epsilon_edges
