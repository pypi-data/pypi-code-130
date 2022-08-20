"""This module provides methods to transform grammars to finite automata et vice versa

"""
from formgram.grammars.types import GrammarDict
from formgram.machines.finite_automata.transformations import to_deterministic
from formgram.grammars.helper_functions.decorators import deepcopy_arguments


@deepcopy_arguments
def to_right_regular_grammar(machine: dict) -> GrammarDict:
    """Create a grammar dictionary from a finite automaton

    The resulting grammar is of a form required by the grammars package.

    :param machine:
    :return: a new right regular grammar dict
    """
    machine = to_deterministic(machine)
    starting_symbol = machine["starting_nodes"][0]
    nonterminals = machine["nodes"]
    productions = set()
    if starting_symbol in machine["accepting_nodes"]:
        productions.add(((starting_symbol,), ()))

    for edge in machine["edges"]:
        (source, symbol, target) = edge
        rule = ((source,), (symbol, target))
        accepting_rule = ((source,), (symbol,))
        productions.add(rule)
        if target in machine["accepting_nodes"]:
            productions.add(accepting_rule)

    return {
        "nonterminals": nonterminals,
        "terminals": machine["alphabet"],
        "starting_symbol": starting_symbol,
        "productions": productions,
    }


@deepcopy_arguments
def from_right_regular_grammar(grammar: GrammarDict) -> dict:
    """Creates a nondeterministic finite automaton from given grammar dict

    :param grammar:
    :return: A nondeterministic finite automaton dictionary
    """
    accepting_nodes = set()
    edges = set()

    acceptor_node = "accepting_node"
    if acceptor_node in grammar["nonterminals"]:
        i = 2
        while f"{acceptor_node}_{i}" in grammar["nonterminals"]:
            i += 1
        acceptor_node = f"{acceptor_node}_{i}"

    for production in grammar["productions"]:
        ((left_nonterminal,), right_hand_side) = production
        if len(right_hand_side) == 0:
            accepting_nodes.add(left_nonterminal)
        elif len(right_hand_side) == 1:
            (symbol,) = right_hand_side
            accepting_nodes.add(acceptor_node)
            edges.add((left_nonterminal, symbol, acceptor_node))
        else:
            (symbol, right_nonterminal) = right_hand_side
            edges.add((left_nonterminal, symbol, right_nonterminal))

    return {
        "nodes": grammar["nonterminals"] | accepting_nodes,
        "alphabet": grammar["terminals"],
        "starting_nodes": {grammar["starting_symbol"]},
        "accepting_nodes": accepting_nodes,
        "edges": edges,
    }
