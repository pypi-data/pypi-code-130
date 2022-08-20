"""This module provides functions to determine certain forms of type 0 grammars

It is assumed in this module that grammars are as described in :ref:`the package description <grammar description>`.
"""

from typing import Mapping, Set, Tuple

from formgram.grammars.helper_functions.production_grouping import group_right_hand_sides_by_left_hand_sides
from formgram.grammars.helper_functions.set_functions import find_new_unique_string
from formgram.grammars.types import GrammarDict, Symbol, Side


def find_new_nonterminal(grammar: GrammarDict, base_symbol: Symbol) -> Symbol:
    """This function finds a name for a new non-terminal using a base symbol

    This function uses a base symbol for finding a new non-terminal.
    The base symbol will be cast to type `str` to form `base`
    The new name will be `<base>_<number>` where number will be the smallest
    possible. If the base string is not in the grammar it will be used instead

    :param grammar:
    :param base_symbol:
    :return: A new nonterminal for the grammar

    :example:
        >>> non_terminals = ["Start"]
        >>> example_grammar = {"nonterminals": non_terminals, ...}
        >>> find_new_nonterminal(example_grammar, "new")
        "new"
        >>> a = find_new_nonterminal(example_grammar, "Start")
        >>> a
        "Start_2"
        >>> example_grammar["nonterminals"].append(a)
        >>> example_grammar["nonterminals"]
        ["Start", "Start_2"]
        >>> find_new_nonterminal(example_grammar, "Start")
        "Start_3"
    """
    return find_new_unique_string(grammar["nonterminals"] | grammar["terminals"], base_symbol)


def _escape_string(string: str) -> str:
    """Escape all control symbols in string

    :example:
        >>> grammar_string = "<S> ::= 'a'"
        >>> _escape_string(grammar_string)
        "\\<S\\> ::= \\\'a\\\'"

    :param string:
    :return: String with all control symbols escaped
    """

    protected_symbols = ["'", '"', "<", ">", "\\"]
    return "".join((s if s not in protected_symbols else "\\"+s for s in string))


def _wrap_each_symbol_in_correct_delimiters(grammar: GrammarDict, side: Side) -> str:
    """Wraps each symbol of a side with Backus Naur form appropriate symbols

    :param side:
    :return: Symbol string, delimited by ticks or brackets
    """
    symbol_strings = []
    for symbol in side:
        if symbol in grammar["terminals"]:
            symbol_strings.append(f"'{_escape_string(str(symbol))}'")
        else:
            symbol_strings.append(f"<{_escape_string(str(symbol))}>")
    return " ".join(symbol_strings)


def _create_backus_naur_line(left_hand_side: Side, right_hand_sides: Set[Side], grammar: GrammarDict) -> str:
    """Create single backus naur line from one left and all right hand sides

    :param left_hand_side:
    :param right_hand_sides:
    :param grammar:
    :return: single line of Backus Naur form
    """
    left_hand_string = _wrap_each_symbol_in_correct_delimiters(grammar, left_hand_side)
    right_hand_strings = (_wrap_each_symbol_in_correct_delimiters(grammar, side) for side in sorted(right_hand_sides))
    right_hand_string = ' | '.join(right_hand_strings)
    return f"{left_hand_string} ::= {right_hand_string}"


def to_backus_naur_form(grammar: GrammarDict) -> str:
    """This function creates a string representation of the grammar

    The string representation is a variation on the backus naur form.
    It uses the same backus naur form variation which is used to parse grammars
    from string in the str_interface subpackage.

    Note that the string representation casts all the symbols to string, if the
    symbol objects of the grammar do not support this an exception will be raised.

    .. warning:
        Also as the str_interface subpackage assumes that the first production
        uses the starting symbol as left hand side, this function will not work
        if there is no such production.
        The assumption is made that a grammar of only unreachable productions
        will not occur, so that this special case can be safely ignored.

    :param grammar:
    :return:
    """

    grouped_productions = group_right_hand_sides_by_left_hand_sides(
        grammar["productions"]
    )
    output_dictionary = {}
    starting_left_hand_side = None
    for left_hand_side in grouped_productions.keys():
        if len(left_hand_side) == 1 and left_hand_side[0] == grammar["starting_symbol"]:
            starting_left_hand_side = left_hand_side
        right_hand_sides = grouped_productions[left_hand_side]
        output_dictionary[left_hand_side] = _create_backus_naur_line(left_hand_side, right_hand_sides, grammar)
    if starting_left_hand_side is None:
        raise ValueError(
            f"The provided grammar {grammar} has no production with a single starting-symbol "
            f"as left hand side"
        )
    starting_string = output_dictionary[starting_left_hand_side]
    output_string = "\n".join(
        {
            value
            for key, value in sorted(output_dictionary.items())
            if key != starting_left_hand_side
        }
    )
    return "\n".join([starting_string, output_string])
