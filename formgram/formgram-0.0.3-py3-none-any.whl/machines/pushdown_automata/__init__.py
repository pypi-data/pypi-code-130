"""This package provides functionality for pushdown automata

Pushdown automaton
==================
.. _pda description:

For this package a pushdown automaton is of type :class:`dict`

Keys
----

* states :class:`Set[str]`
    the set of all states
* accepting_states :class:`Set[str]`
    the subset of `states` which accept
* starting_state :class:`str`
    the element of `states` which is the internal state of the automaton when it is started
* alphabet :class:`Set[str]`
    the set of symbols from which the words can be created which are to be decided
* stack_alphabet :class:`Set[str]`
    the set of symbols which can be written to the stack
* initial_stack_symbol :class:`str`
    the element of `stack_alphabet` which is the only symbol in the stack when the automaton is started
* transitions :class:`Set[Tuple[str, str | None, str, str, Tuple[str]]]`
    the rules with which the automaton works.


Transitions
-----------

The transitions are ordered
``source_state, read_symbol, stack_head, target_state, stack_push``
where

* source_state
    is element of ``states``
* read_symbol
    is element of ``alphabet`` or ``None``
* stack_head
    is element of ``stack_alphabet``
* target_state
    is element of ``states``
* stack_push
    is a possibly empty :class:`tuple` of elements of ``stack_alphabet``


"""


