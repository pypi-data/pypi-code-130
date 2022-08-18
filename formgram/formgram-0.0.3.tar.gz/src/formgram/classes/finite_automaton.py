"""This module provides a class for finite automata

"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Sequence, Set, TypeVar

import formgram.classes.grammar as grammar_classes
from formgram.machines.finite_automata.classifiers import is_total, is_deterministic
from formgram.machines.finite_automata.grammar_interface import from_right_regular_grammar
from formgram.machines.finite_automata.simulation_functions import does_accept
from formgram.machines.finite_automata.transformations import to_deterministic

SelfFiniteAutomaton = TypeVar("SelfFiniteAutomaton", bound="FiniteAutomatonData")


@dataclass
class FiniteAutomatonData:
    """Container for all internal values for any finite automaton

    As it is frozen all internal values for any finite automaton are fixed,
    """
    nodes: Set[str]
    starting_nodes: Set[str]
    accepting_nodes: Set[str]
    alphabet: Set[str]
    edges: Set[Tuple[str, str, str]]

    @classmethod
    def from_dict(cls: type[SelfFiniteAutomaton], automata_dict: dict) -> SelfFiniteAutomaton:
        """Create a new FiniteAutomaton from dict

        :param automata_dict:
        :return:
        """
        return cls(**automata_dict)

    @classmethod
    def from_grammar(cls: type[SelfFiniteAutomaton], grammar_object: grammar_classes.RegularGrammar) -> SelfFiniteAutomaton:
        """Create a new FiniteAutomaton from RegularGrammar object

        :param grammar_object:
        :return:
        """
        return cls.from_dict(from_right_regular_grammar(grammar_object.to_right_regular_form().to_dict()))

    def to_dict(self) -> dict:
        """Create dictionary representation of this finite automaton

        :return:
        """
        return {
            "nodes": self.nodes,
            "starting_nodes": self.starting_nodes,
            "accepting_nodes": self.accepting_nodes,
            "alphabet": self.alphabet,
            "edges": self.edges,
        }


class FiniteAutomaton(FiniteAutomatonData):
    """A finite automaton.

    Any background simulation assumes nondeterministic automata and thus works
    with deterministic and nondeterministic automata alike.
    """

    def does_accept(self, word: Sequence[str]) -> bool:
        """Simulate the automaton on word

        :param word:
        :return:
        """
        return does_accept(machine=self.to_dict(), word=word)

    def is_total(self) -> bool:
        """Check if all nodes have edges for all symbols

        :return:
        """
        return is_total(machine=self.to_dict())

    def is_deterministic(self) -> bool:
        """Check if no duplicate or epsilon edges exist

        :return:
        """
        return is_deterministic(machine=self.to_dict())

    def to_deterministic(self) -> FiniteAutomaton:
        """Create equivalent deterministic finite automaton

        :return:
        """
        return FiniteAutomaton.from_dict(to_deterministic(self.to_dict()))
