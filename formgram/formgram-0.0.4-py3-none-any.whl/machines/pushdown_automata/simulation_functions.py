"""This module provides functions to simulate any given push down automaton

For the structure of those automata look at the package description
"""

from typing import Sequence, Tuple

from formgram.machines.pushdown_automata.grammar_interface import nest_push_down_automata_transitions


def simulate_single_epsilon_step(
    transition_dict: dict, current_state: str, stack: Tuple[str]
) -> set:
    """

    :param transition_dict:
    :param current_state:
    :param stack:
    :return:
    """
    if not stack:
        return set()
    stack_head, *stack_tail = stack
    options = transition_dict.get(current_state, {}).get(None, {}).get(stack_head, set())
    return {
        (new_state, (insert_to_stack if insert_to_stack else ()) + tuple(stack_tail))
        for (new_state, insert_to_stack) in options
    }


def simulate_arbitrary_epsilon_steps(transition_dict: dict, combinations: set) -> set:
    """

    :param transition_dict:
    :param combinations:
    :return:
    """
    reached_combinations = combinations.copy()
    unexplored_combinations = combinations.copy()
    while unexplored_combinations:
        _state, _stack = unexplored_combinations.pop()
        new_combinations = simulate_single_epsilon_step(
            transition_dict, _state, _stack
        ).difference(reached_combinations)
        unexplored_combinations.update(new_combinations)
        reached_combinations.update(new_combinations)
    return reached_combinations


def simulate_single_symbol_step(
    transition_dict: dict, current_state: str, read_symbol: str, stack: Tuple[str]
) -> set:
    """

    :param transition_dict:
    :param current_state:
    :param read_symbol:
    :param stack:
    :return:
    """
    if not stack:
        return set()
    stack_head, *stack_tail = stack
    options = (
        transition_dict.get(current_state, {}).get(read_symbol, {}).get(stack_head, set())
    )
    return {
        (new_state, (insert_to_stack if insert_to_stack else ()) + tuple(stack_tail))
        for (new_state, insert_to_stack) in options
    }


def simulate_single_step(transition_dict: dict, combinations: set, read_symbol: str) -> set:
    """

    :param transition_dict:
    :param combinations:
    :param read_symbol:
    :return:
    """
    epsilon_hull = simulate_arbitrary_epsilon_steps(transition_dict, combinations)
    single_symbol_step = {
        combination
        for state, stack in epsilon_hull
        for combination in simulate_single_symbol_step(
            transition_dict, state, read_symbol, stack
        )
    }
    return simulate_arbitrary_epsilon_steps(transition_dict, single_symbol_step)


def run_full_simulation(
    machine: dict, input_tape: Sequence[str], state_accepting: bool = False
) -> bool:
    """


    :param machine:
    :param input_tape:
    :param state_accepting:
    :return:
    """
    transition_dict = nest_push_down_automata_transitions(machine["transitions"])
    options = simulate_arbitrary_epsilon_steps(
        transition_dict,
        {(machine["starting_state"], (machine["initial_stack_symbol"],))},
    )
    for symbol in input_tape:
        options = simulate_single_step(transition_dict, options, symbol)

        if not options:
            return False
    if state_accepting:
        for (state, _) in options:
            if state in machine["accepting_states"]:
                return True
        return False
    else:
        for (_, stack) in options:
            if not stack:
                return True
        return False
