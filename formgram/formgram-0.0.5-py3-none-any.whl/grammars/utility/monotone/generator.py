"""This module provides a function to generate words from any monotone grammar

.. note::
    Grammars of a higher Chomsky hierarchy type are transformed to be monotone
    for the algorithm.

"""

from typing import Sequence, Set, Dict

from formgram.grammars.classifiers.chomsky_classifiers import is_context_free
from formgram.grammars.helper_functions.production_grouping import group_right_hand_sides_by_left_hand_sides
from formgram.grammars.transformations.context_free import to_monotone_start_form, to_epsilon_free_form
from formgram.grammars.types import Side, Symbol, GrammarDict


def apply_grouped_productions_to_word(word: Sequence[Symbol],
                                      grouped_productions: Dict[Side, Set[Side]]) -> Set[Sequence[Symbol]]:
    """Return the set of words producible by applying any possible production on the given word

    :param word:
    :param grouped_productions:
    :return: set of all words directly producible from given word with given productions
    """
    output = set()
    indices = range(len(word))
    for start in indices:
        for end in [index + 1 for index in indices if index >= start]:
            subword = word[start:end]
            if subword in grouped_productions:
                new_words = {
                    word[:start] + replacement + word[end:]
                    for replacement in grouped_productions[subword]
                }
                output.update(new_words)
    return output


def generate_words_limited_by_length(grammar: GrammarDict, max_length: int) -> Set[Sequence[Symbol]]:
    """Generate all words the grammar can produce with length shorter or equal to max_length

    :param grammar:
    :param max_length:
    :return: Set of all generatable words shorter than max_length
    """
    if is_context_free(grammar):
        grammar = to_monotone_start_form(grammar)
        grammar = to_epsilon_free_form(grammar)
    grouped_sides = group_right_hand_sides_by_left_hand_sides(grammar["productions"])
    current_words = {(grammar["starting_symbol"],)}
    reached_words = current_words.copy()
    while any({len(word) <= max_length for word in current_words}):
        to_iterate = {
            word
            for word in current_words
            if any({symbol not in grammar["terminals"] for symbol in word})
        }
        # to_iterate = current_words
        current_words = set()
        for word in to_iterate:
            creatable_words = apply_grouped_productions_to_word(word, grouped_sides)
            current_words.update(creatable_words)
        current_words.difference_update(reached_words)
        reached_words.update(current_words)
    return {
        word
        for word in reached_words
        if len(word) <= max_length
        and all({symbol in grammar["terminals"] for symbol in word})
    }
