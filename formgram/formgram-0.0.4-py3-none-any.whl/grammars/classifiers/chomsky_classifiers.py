"""This module provides functions for chomsky classification of grammars

It is assumed in this module that grammars are as described in :ref:`the package description <grammar description>`.

:example:
    >>> from formgram.grammars.classifiers.chomsky_classifiers import get_chomsky_type
    >>> alphabet = {"a", }
    >>> variables = {"A", "S"}
    >>> starting_symbol = "S"
    >>> productions = [
    >>>     (("S",), ("A",)),
    >>>     (("A",), ("a", "A")),
    >>>     (("A",), ("a",))
    >>> ]
    >>> grammar = {
    >>>     "terminals": alphabet,
    >>>     "nonterminals": variables,
    >>>     "starting_symbol": starting_symbol,
    >>>     "productions": productions
    >>> }
    >>> get_chomsky_type(grammar)
    <ChomskyType.REGULAR: 3>
"""


from enum import IntEnum
from typing import Tuple

from formgram.grammars.helper_functions.input_validator import validate_grammar_form
from formgram.grammars.helper_functions.sequence_functions import get_common_prefix, get_common_suffix
from formgram.grammars.types import GrammarDict, Production, Alphabet


class ChomskyType(IntEnum):
    """Provide a nice printable way to express Chomsky type

    The IntEnum class makes sure ChomskyType.MONOTONE == 1 evaluates True.
    However: print(ChomskyType.MONOTONE) will not print 1 but
    "ChomskyType.MONOTONE" which can easier to read.
    """

    REGULAR = 3
    CONTEXT_FREE = 2
    MONOTONE = 1
    UNRESTRICTED = 0


def get_chomsky_type(grammar: GrammarDict) -> ChomskyType:
    """Determine the chomsky type of given grammar

    This function calls the specific determining functions for all chomsky types
    in descending order.

    :param grammar: A Mapping as described in module description
    :return ChomskyType: An IntEnum between 0 and 3 named appropriately
    :raise:
        :TypeError: If the provided object does not provide the necessary methods
            needed by other functions of this project
        :ValueError: If the provided object is otherwise not of correct form for
            a Chomsky-Grammar
    """
    validate_grammar_form(grammar)
    if is_single_side_linear(grammar):
        return ChomskyType.REGULAR
    if is_context_free(grammar):
        return ChomskyType.CONTEXT_FREE
    if is_monotone(grammar):
        return ChomskyType.MONOTONE
    return ChomskyType.UNRESTRICTED


def is_grammar(grammar: GrammarDict) -> bool:
    """Check if given dict conforms meets package requirements for grammars

    The correct form is defined in the module description.

    :param grammar: The object to check for grammar form
    :return bool: True if grammar is of correct form else False
    """
    try:
        validate_grammar_form(grammar)
    except (TypeError, ValueError):
        return False
    return True


def is_monotone(grammar: GrammarDict, allow_starting_epsilon_productions: bool = True) -> bool:
    """Determine if production right hand sides are longer then left hand ones

    This is done by comparing the left and right hand sides of every single
    production individually.

    If the :attr:`allow_starting_epsilon_productions` flag is set, the special case of
    epsilon productions is handled by :func:`check_for_epsilon_special_case`

    :param grammar: The grammar to determine monotonicity of
    :param allow_starting_epsilon_productions: If this flag is set, monotonicity
        is allowed to be violated by productions with only the starting-symbol
        as their left hand side, under the condition, that the starting-symbol
        may not occur on any right hand side
    :return: True if no left hand side is longer than the corresponding right
        hand one
    """
    for left_hand_side, right_hand_side in grammar["productions"]:
        if len(right_hand_side) == 0 and allow_starting_epsilon_productions:
            continue  # skip if starting symbols may produce the emtpy word
        if len(left_hand_side) > len(right_hand_side):
            return False

    if allow_starting_epsilon_productions:
        return check_for_epsilon_special_case(grammar)
    else:
        return True


def replaces_exactly_one_non_terminal(production: Production,
                                      non_terminals: Alphabet) -> bool:
    """Check if the left hand side is present on the right hand side sans exactly one nonterminal

    This is done by looking for each nonterminal in the left hand side:
    Are all the previous symbols a prefix of the right hand side
    and all following symbols a suffix of the right hand side?

    :param production: The production to be checked
    :param non_terminals: The Collection of non-terminal symbols
    :return: True if one can describe the left hand side though
        (common_prefix + one_non_terminal + common_suffix) else False
    """
    left_hand_side, right_hand_side = production
    left_non_terminals_enumerated = (
        (index, symbol)
        for index, symbol in enumerate(left_hand_side)
        if symbol in non_terminals
    )
    common_prefix = get_common_prefix(left_hand_side, right_hand_side)
    common_suffix = get_common_suffix(left_hand_side, right_hand_side)
    left_hand_length = len(left_hand_side)
    common_prefix_len, common_suffix_len = map(len, [common_prefix, common_suffix])
    for index, symbol in left_non_terminals_enumerated:
        # can deconstruct the left hand side into
        # prefix symbol suffix
        # now check if prefix in common prefix and suffix in common suffix.
        if (
            common_prefix_len >= index
            and common_suffix_len >= left_hand_length - index - 1
        ):  # - 1 as the non terminal itself must be considered
            return True
    return False


def is_context_free(grammar: GrammarDict) -> bool:
    """Determine if grammar is context free

    This means that the left hand side must be exactly one non-terminal

    :param grammar: The grammar to determine context-freedom of
    :return: True if grammar is context free else False
    """
    for left_hand_side, _ in grammar["productions"]:
        if len(left_hand_side) != 1 or left_hand_side[0] not in grammar["nonterminals"]:
            return False
    return True


def is_single_side_linear(grammar: GrammarDict) -> bool:
    """Determine if grammar is left or right linear

    For a grammar to be type 3 it first must be context free.
    Secondly it must be left linear or right linear, meaning that every
    right hand side of every production must have at most one non-terminal symbol
    which all must be either the left most or right most symbol.

    It is not allowed to mix left and right linear productions, which would make
    the grammar more expressive then type 3. Thus making it only linear which is
    a strict subset of context free languages but a strict superset of regular
    ones.

    :param grammar: The grammar to determine linearity of
    :return: True if the grammar is any kind of linear else False
    """
    if not is_context_free(grammar):
        return False
    return is_left_linear(grammar) or is_right_linear(grammar)


def is_left_linear(grammar: GrammarDict) -> bool:
    """Determine if grammar is left linear

    For a grammar to be left linear it must be context-free.
    Additionally every production must have at most one non-terminal symbol in
    each right hand side. In these right hand sides the nonterminals must be
    the leftmost symbol.

    :param grammar: The grammar to determine left linearity of
    :return: True if grammar is left linear else False
    """
    if not is_context_free(grammar):
        return False
    for _, right_hand_side in grammar["productions"]:
        if not right_hand_side:
            continue  # the empty word has at most one terminal!
        leftmost_symbol, *symbols = right_hand_side
        if any(symbol in grammar["nonterminals"] for symbol in symbols):
            return False  # only the leftmost symbol is allowed to be non-terminal
        if not symbols and leftmost_symbol not in grammar["terminals"]:
            return False  # there must be terminals

    return True


def is_right_linear(grammar: GrammarDict) -> bool:
    """Determine if grammar is right linear

    For a grammar to be right linear, it must be context free.
    Additionally every production must have at most one non-terminal symbol in
    each right hand side. In these right hand sides the nonterminals must be
    the rightmost symbol.

    :param grammar: The grammar to determine right linearity of
    :return: True if grammar is right linear else False
    """
    if not is_context_free(grammar):
        return False
    for _, right_hand_side in grammar["productions"]:
        if not right_hand_side:
            continue  # the empty word has at most one terminal!
        *symbols, rightmost_symbol = right_hand_side
        if any(symbol in grammar["nonterminals"] for symbol in symbols):
            return False  # only the rightmost symbol is allowed to be non-terminal
        if not symbols and rightmost_symbol not in grammar["terminals"]:
            return False  # there must be terminals
    return True


def is_regular(grammar: GrammarDict) -> bool:
    """Determine if grammar is right or left regular

    For a grammar to be regular it must be left- or right linear and every
    right hand side must be of length smaller then two.

    :param grammar: The grammar to determine regularity of
    :return: True if the grammar is regular else False
    """
    return is_left_regular(grammar) or is_right_regular(grammar)


def is_right_regular(grammar: GrammarDict) -> bool:
    """Determine if grammar is right regular

    For a grammar to be right regular it must be right linear with a maximal
    right hand side length of two.

    :param grammar: A context-free grammar to determine right regularity of
    :return: True if right linear with max right hand side of two else False
    """
    if not is_right_linear(grammar):
        return False
    for _, right_hand_side in grammar["productions"]:
        if len(right_hand_side) > 2:
            return False
    return True


def is_left_regular(grammar: GrammarDict) -> bool:
    """Determine if grammar is left regular

    For a grammar to be left regular it must be left linear with a maximal
    right hand side length of two.

    :param grammar: A context-free grammar to determine left regularity of
    :return: True if left linear with max right hand side of two else False
    """
    if not is_left_linear(grammar):
        return False
    for _, right_hand_side in grammar["productions"]:
        if len(right_hand_side) > 2:
            return False
    return True


def check_for_epsilon_special_case(grammar: GrammarDict) -> bool:
    """Check if only the starting symbol can (in-)directly produce the emtpy word

    :param grammar: The grammar to check the epsilon production special case on
    :return: True if only the starting symbol produces the empty word and said
        symbol only ever occurs on the left hand side of productions
    """

    def is_epsilon_production(production: Production):
        """Check if given production has empty right hand side

        :param production:
        :return: True if production right hand side is empty
        """
        left_hand_side, right_hand_side = production
        return len(right_hand_side) == 0

    def is_starting_symbol_production(production: Production):
        """Check if left hand side of production is only the starting symbol

        :param production:
        :return: True if left hand side of production is only the starting symbol
        """
        left_hand_side, right_hand_side = production
        return (
            len(left_hand_side) == 1 and left_hand_side[0] == grammar["starting_symbol"]
        )

    def has_starting_symbol_in_right_hand_side(production: Production):
        """Check if the starting symbol is in the right hand side

        :param production:
        :return: True if any of the right hand symbols is the starting one
        """
        left_hand_side, right_hand_side = production
        return grammar["starting_symbol"] in right_hand_side

    epsilon_productions = {
        production
        for production in grammar["productions"]
        if is_epsilon_production(production)
    }
    if any(
        not is_starting_symbol_production(epsilon_production)
        for epsilon_production in epsilon_productions
    ):
        return False

    if epsilon_productions and any(
        has_starting_symbol_in_right_hand_side(production)
        for production in grammar["productions"]
    ):
        return False

    return True


def is_context_sensitive(grammar: GrammarDict) -> bool:
    """Determine if grammar is of context sensitive form

    This means that the grammar must be monotone and for every production exactly
    one non-terminal of the left hand side must be replaced by a Sequence composed
    of terminals and/or nonterminals

    :param grammar: The grammar to determine context-sensitivity of
    :return: True if each production is context-sensitive
    """
    if not is_monotone(grammar):
        return False
    for production in grammar["productions"]:
        non_terminals = grammar["nonterminals"]
        if not replaces_exactly_one_non_terminal(production, non_terminals):
            return False
    return True
