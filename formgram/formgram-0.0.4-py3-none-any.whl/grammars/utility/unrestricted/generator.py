"""This module provides a function to generate words from any grammar

.. note::
    As this works on any grammar, the amount of steps taken are limited as the
     only way to guarantee halting of the algorithm.

"""
from collections import Set, Sequence

from formgram.grammars.classifiers.chomsky_classifiers import is_context_free
from formgram.grammars.helper_functions.production_grouping import group_right_hand_sides_by_left_hand_sides
from formgram.grammars.transformations.context_free import to_monotone_start_form, to_epsilon_free_form
from formgram.grammars.types import GrammarDict, Symbol
from formgram.grammars.utility.monotone.generator import apply_grouped_productions_to_word


def generate_words_in_limited_steps(grammar: GrammarDict, steps: int) -> Set[Sequence[Symbol]]:
    """Generate all words the grammar can produce with length shorter or equal to max_length

    :param grammar:
    :param steps:
    :return: Set of words producible in given amount of steps
    """
    if is_context_free(grammar):
        grammar = to_monotone_start_form(grammar)
        grammar = to_epsilon_free_form(grammar)
    grouped_sides = group_right_hand_sides_by_left_hand_sides(grammar["productions"])
    current_words = {(grammar["starting_symbol"],)}
    reached_words = current_words.copy()
    for i in range(steps):
        to_iterate = (
            word
            for word in current_words
            if any({symbol not in grammar["terminals"] for symbol in word})
        )
        current_words = set()
        for word in to_iterate:
            creatable_words = apply_grouped_productions_to_word(word, grouped_sides)
            current_words.update(creatable_words)
        current_words.difference_update(reached_words)
        reached_words.update(current_words)

    return {
        word
        for word in reached_words
        if all({symbol in grammar["terminals"] for symbol in word})
    }
