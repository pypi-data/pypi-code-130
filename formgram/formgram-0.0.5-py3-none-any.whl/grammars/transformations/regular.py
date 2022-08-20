"""This module provides functions to determine certain forms of type 3 grammars

It is assumed in this module that grammars are as described in :ref:`the package description <grammar description>`.
"""


from formgram.grammars.classifiers.chomsky_classifiers import is_right_linear, is_left_regular, \
    is_left_linear, is_right_regular
from formgram.grammars.helper_functions.decorators import deepcopy_arguments
from formgram.grammars.transformations.context_free import to_leftbound_start_form, to_epsilon_free_form, \
    to_unit_free_form
from formgram.grammars.types import GrammarDict
from formgram.grammars.utility.unrestricted.helper import find_new_nonterminal


@deepcopy_arguments
def to_right_linear_form(grammar: GrammarDict) -> GrammarDict:
    """Transform a type 3 grammar into right linear form

    This means that only the rightmost symbol of any right hand side may be
    a nonterminal symbol

    :param grammar: A grammar of Type 3
    :return: A right linear grammar
    """
    if is_right_linear(grammar):
        return grammar  # grammar is already of right form

    # make sure there are neither epsilon nor unit productions, and the start symbol is only
    # on the left hand side
    grammar = to_leftbound_start_form(grammar)
    grammar = to_epsilon_free_form(grammar)
    grammar = to_unit_free_form(grammar)

    new_productions = set()
    for production in grammar["productions"]:
        (left_hand_symbol,), right_hand_side = production
        if len(right_hand_side) == 0:
            new_productions.add(production)
        elif (
            right_hand_side[0] not in grammar["nonterminals"]
            or len(right_hand_side) == 1
        ):
            if left_hand_symbol == grammar["starting_symbol"]:
                new_productions.add(production)
            else:
                new_productions.add(
                    (
                        (grammar["starting_symbol"],),
                        (*right_hand_side, left_hand_symbol),
                    )
                )
        else:
            non_terminal, *rest_of_right_hand_side = right_hand_side
            if left_hand_symbol == grammar["starting_symbol"]:
                new_productions.add(((non_terminal,), (*rest_of_right_hand_side,)))
            else:
                new_productions.add(
                    ((non_terminal,), (*rest_of_right_hand_side, left_hand_symbol))
                )
    return {
        "terminals": grammar["terminals"],
        "nonterminals": grammar["nonterminals"],
        "productions": new_productions,
        "starting_symbol": grammar["starting_symbol"],
    }


@deepcopy_arguments
def to_left_linear_form(grammar: GrammarDict) -> GrammarDict:
    """Transform a type 3 grammar into left linear form

    This means that only the leftmost symbol of any right hand side may be
    a nonterminal symbol

    :param grammar: A grammar of Type 3
    :return: A left linear grammar
    """
    if is_left_linear(grammar):
        return grammar  # grammar is already left linear

    # here the grammar is clearly right linear, as it is type 3 and not left linear

    # make sure there are neither epsilon nor unit productions, and the start symbol is only
    # on the left hand side
    grammar = to_leftbound_start_form(grammar)
    grammar = to_epsilon_free_form(grammar)
    grammar = to_unit_free_form(grammar)

    new_productions = set()
    for production in grammar["productions"]:
        (left_hand_symbol,), right_hand_side = production
        if len(right_hand_side) == 0:
            new_productions.add(production)
        elif (
            right_hand_side[-1] not in grammar["nonterminals"]
            or len(right_hand_side) == 1
        ):
            if left_hand_symbol == grammar["starting_symbol"]:
                new_productions.add(production)
            else:
                new_productions.add(
                    (
                        (grammar["starting_symbol"],),
                        (left_hand_symbol, *right_hand_side),
                    )
                )
        else:
            *rest_of_right_hand_side, non_terminal = right_hand_side
            if left_hand_symbol == grammar["starting_symbol"]:
                new_productions.add(((non_terminal,), (*rest_of_right_hand_side,)))
            else:
                new_productions.add(
                    ((non_terminal,), (left_hand_symbol, *rest_of_right_hand_side))
                )
    return {
        "terminals": grammar["terminals"],
        "nonterminals": grammar["nonterminals"],
        "productions": new_productions,
        "starting_symbol": grammar["starting_symbol"],
    }


@deepcopy_arguments
def to_left_regular_form(grammar: GrammarDict) -> GrammarDict:
    """Transform a type 3 grammar into left regular form

    This means that only the leftmost symbol of any right hand side may be
    a nonterminal symbol. And every right hand side must be shorter then length three.

    :param grammar: A grammar of Type 3
    :return: A left regular grammar
    """
    if is_left_regular(grammar):
        return grammar
    if not is_left_linear(grammar):
        grammar = to_left_linear_form(grammar)

    new_productions = set()
    new_nonterminals = set()
    for left_hand_side, right_hand_side in grammar["productions"]:
        if len(right_hand_side) < 3:
            new_productions.add((left_hand_side, right_hand_side))
        else:
            remainder = right_hand_side
            last_nonterminal = left_hand_side[0]
            while len(remainder) > 2:
                *remainder, tail_symbol = remainder
                base_symbol = f"{left_hand_side}_({', '.join(remainder)})"
                new_symbol = find_new_nonterminal(
                    grammar=grammar, base_symbol=base_symbol
                )
                new_productions.add(((last_nonterminal,), (new_symbol, tail_symbol)))
                new_nonterminals.add(new_symbol)
                last_nonterminal = new_symbol
    return {
        "terminals": grammar["terminals"],
        "nonterminals": new_nonterminals.union(grammar["nonterminals"]),
        "productions": new_productions,
        "starting_symbol": grammar["starting_symbol"],
    }


@deepcopy_arguments
def to_right_regular_form(grammar: GrammarDict) -> GrammarDict:
    """Transform a type 3 grammar into right regular form

    This means that only the rightmost symbol of any right hand side may be
    a nonterminal symbol. And every right hand side must be shorter then length three.

    :param grammar: A grammar of Type 3
    :return: A right regular grammar
    """
    if is_right_regular(grammar):
        return grammar
    if not is_right_linear(grammar):
        grammar = to_right_linear_form(grammar)

    new_productions = set()
    new_nonterminals = set()
    for left_hand_side, right_hand_side in grammar["productions"]:
        if len(right_hand_side) < 3:
            new_productions.add((left_hand_side, right_hand_side))
        else:
            remainder = right_hand_side
            last_nonterminal = left_hand_side[0]
            while len(remainder) > 2:
                head_symbol, *remainder = remainder
                base_symbol = f"{left_hand_side}_({', '.join(remainder)})"
                new_symbol = find_new_nonterminal(
                    grammar=grammar, base_symbol=base_symbol
                )
                new_productions.add(((last_nonterminal,), (head_symbol, new_symbol)))
                new_nonterminals.add(new_symbol)
                last_nonterminal = new_symbol
    return {
        "terminals": grammar["terminals"],
        "nonterminals": new_nonterminals.union(grammar["nonterminals"]),
        "productions": new_productions,
        "starting_symbol": grammar["starting_symbol"],
    }
