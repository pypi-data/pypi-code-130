"""This module provides functions to create a pushdown automata from a grammar and vice versa

"""

from itertools import product
from typing import Collection, Iterator, Tuple, Dict

from formgram.grammars.helper_functions.decorators import deepcopy_arguments
from formgram.grammars.transformations.context_free import to_greibach_normal_form, to_clean_form
from formgram.grammars.types import GrammarDict


def from_context_free_grammar(grammar: dict, only_state_name: str = "q") -> dict:
    """Create a PDA with only one state from a context free grammar

    :param only_state_name: The name of the one state the resulting PDA has
    :param grammar:
    :return: a new pushdown automaton
    """
    grammar = to_greibach_normal_form(grammar)
    transition_tuples = set()
    for production in grammar["productions"]:
        (nonterminal,), right_hand_side = production
        if not len(right_hand_side):
            terminal, nonterminals = None, None
        else:
            terminal, *nonterminals = right_hand_side
        nonterminals = tuple(nonterminals) if nonterminals else None
        original_state = new_state = only_state_name
        transition_tuples.add((original_state, terminal, nonterminal, new_state, nonterminals))

    return {
        "accepting_states": {only_state_name},
        "initial_stack_symbol": grammar["starting_symbol"],
        "transitions": transition_tuples,
        "starting_state": only_state_name,
        "states": {only_state_name},
        "alphabet": grammar["terminals"],
        "stack_alphabet": grammar["nonterminals"],
    }


def nest_push_down_automata_transitions(transition_tuples: Collection[tuple]) -> Dict[str, Dict[str, Dict[str, Tuple[str, Tuple[str, ...]]]]]:
    """Create a transition dict for push down automata from a list of transition tuples

    :param transition_tuples:
    :return: a nested dict representing the transitions
    """
    transitions = {}
    for original_state, read_symbol, stack_head, new_state, stack_push in transition_tuples:
        if original_state not in transitions:
            transitions[original_state] = {}
        if read_symbol not in transitions[original_state]:
            transitions[original_state][read_symbol] = {}
        if stack_head not in transitions[original_state][read_symbol]:
            transitions[original_state][read_symbol][stack_head] = set()
        transitions[original_state][read_symbol][stack_head].add((new_state, stack_push))
    return transitions


def flatten_push_down_automata_transition_dictionary(transitions: dict) -> Iterator[Tuple[str, str, str, str, Tuple[str, ...]]]:
    """Generate tuples for each transition in the nested transition dict

    :param transitions:
    :return: An Iterator yielding a single tuple per transition
    """
    for old_state in transitions:
        read_symbol_mapping = transitions[old_state]
        for read_symbol in read_symbol_mapping:
            stack_head_mapping = read_symbol_mapping[read_symbol]
            for stack_head in stack_head_mapping:
                for next_state, stack_push in stack_head_mapping[stack_head]:
                    yield old_state, read_symbol, stack_head, next_state, stack_push


def nonterminal(source_state: str, stack_head: str, target_state: str) -> str:
    """Create a new nonterminal based on template

    Using this function guarantees that for any triple of
    source_state, stack_head and target_state
    the resulting new nonterminal string is identical and unique compared to every
    other triple.

    :param source_state:
    :param stack_head:
    :param target_state:
    :return: a new nonterminal string
    """
    return f"[{source_state}, {stack_head}, {target_state}]"


def create_possible_right_hand_side_tails(stack_push, states, first_state, last_state) -> Iterator[tuple]:
    """Generate all possible sate sequences which start with first_state, end with last_state and are of same length as stack_push

    :param stack_push:
    :param states:
    :param first_state:
    :param last_state:
    :return: Iterator yielding sequences from first_state to last_state as tuple
    """
    if not stack_push:
        return  # stop iteration

    if len(stack_push) == 1:
        yield tuple([nonterminal(first_state, stack_push[0], last_state)])
        return

    possible_state_sequences = product(states, repeat=len(stack_push) - 1)
    for sequence in possible_state_sequences:
        head = (nonterminal(first_state, stack_push[0], sequence[0]),)
        middle = tuple(nonterminal(sequence[i], stack_push[i+1], sequence[i+1]) for i in range(0, len(sequence) - 1))
        tail = (nonterminal(sequence[-1], stack_push[-1], last_state),)
        yield head + tuple(middle) + tail


@deepcopy_arguments
def to_context_free_grammar(push_down_automaton: dict) -> GrammarDict:
    """Create a context free grammar from given push down automaton

    Essentially this grammar simulates the stack by saving the stack entries in the nonterminals

    The book :cite:t`hopcroft2006automata` describes this at length in section `6.3.2`

    :param push_down_automaton:
    :return: new context free grammar dict
    """
    starting_symbol = "S"

    nonterminals = {
        nonterminal(state, stack_head, other_state)
        for state in push_down_automaton["states"]
        for stack_head in push_down_automaton["stack_alphabet"]
        for other_state in push_down_automaton["states"]
    } | {starting_symbol}

    productions = set()
    for state in push_down_automaton["states"]:
        left_hand_side = (starting_symbol,)
        starting_state = push_down_automaton['starting_state']
        initial_stack_head = push_down_automaton['initial_stack_symbol']
        right_hand_side = (nonterminal(starting_state, initial_stack_head, state), )
        starting_configuration_production = (left_hand_side, right_hand_side)
        productions.add(starting_configuration_production)

    transition_tuples = push_down_automaton["transitions"]
    for original_state, read_symbol, stack_head, next_state, stack_push in transition_tuples:
        target_state_to_left_hand_symbol_mapping = {
            target_state: nonterminal(original_state, stack_head, target_state)
            for target_state in push_down_automaton["states"]
        }

        right_hand_head = (read_symbol,) if read_symbol is not None else ()
        for target_state, left_hand_symbol in target_state_to_left_hand_symbol_mapping.items():
            left_hand_side = (left_hand_symbol,)
            if not stack_push:
                production = (left_hand_side, right_hand_head)
                productions.add(production)
            else:
                right_hand_tails = create_possible_right_hand_side_tails(
                        stack_push, push_down_automaton["states"], next_state, target_state
                    )
                right_hand_sides = (right_hand_head + tail for tail in right_hand_tails)
                for right_hand_side in right_hand_sides:
                    production = (left_hand_side, right_hand_side)
                    productions.add(production)

    new_grammar = {
        "nonterminals": nonterminals,
        "terminals": push_down_automaton["alphabet"],
        "starting_symbol": starting_symbol,
        "productions": productions,
    }
    return to_clean_form(new_grammar)
