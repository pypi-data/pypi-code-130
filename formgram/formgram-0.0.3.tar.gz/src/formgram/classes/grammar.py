"""This module provides grammar classes for easy usage

The classes are structured hierarchical, as to only show methods which can be
used on the given Chomsky hierarchy level.

.. warning::
    The classes themself do NOT check if the provided grammar is of correct
    type. One can initialize a :class:`MonotoneGrammar` with non-monotone
    transitions. Note that in this case the methods are not guaranteed to work

.. note::
    Due to not checking correctness of hierarchy level, it is highly suggested
    to initialize via :class:`Grammar` and use
    :py:meth:`.to_correct_chomsky_hierarchy_level`
    to create a new object of the highest satisfied hierarchy level.

"""

from __future__ import annotations
from typing import MutableSet, Union, TypeVar, Set, Tuple
from dataclasses import dataclass

from formgram.classes.finite_automaton import FiniteAutomaton
from formgram.classes.pushdown_automaton import PushdownAutomaton
from formgram.classes.turing_machine import TuringMachine
from formgram.grammars.classifiers.chomsky_classifiers import get_chomsky_type, ChomskyType
from formgram.grammars.helper_functions.input_validator import validate_grammar_form
from formgram.grammars.transformations.context_free import to_chomsky_normal_form, to_greibach_normal_form
from formgram.grammars.transformations.monotone import to_context_sensitive_form
from formgram.grammars.transformations.regular import to_left_linear_form, to_right_linear_form, \
    to_left_regular_form, to_right_regular_form
from formgram.grammars.str_interface.backus_naur_parser import parse
from formgram.grammars.utility.monotone.generator import generate_words_limited_by_length
from formgram.grammars.utility.unrestricted.generator import generate_words_in_limited_steps
from formgram.grammars.utility.unrestricted.helper import to_backus_naur_form
from formgram.machines.finite_automata.grammar_interface import to_right_regular_grammar
from formgram.machines.pushdown_automata.grammar_interface import to_context_free_grammar
import formgram.machines.turing_machines.grammar_interface as turing_interface

# In Python 3.11 one would use Self from typing_extensions
# This is the previous correct version as described in PEP 673

SelfData = TypeVar("SelfData", bound="GrammarData")
SelfGrammar = TypeVar("SelfGrammar", bound="Grammar")


@dataclass(frozen=True)
class GrammarData:
    """Container for all internal values for any Grammar

    As it is frozen all internal values for any Grammar are fixed,
    preventing ch
    """
    terminals: frozenset[str]
    nonterminals: frozenset[str]
    starting_symbol: str
    productions: frozenset[tuple[str]]

    def __post_init__(self):
        """Make sure that the sets cant be altered after initialisation"""
        validate_grammar_form(self.__dict__)
        immutable_keys = ("terminals", "nonterminals", "productions")  # could be sets
        if any((isinstance(self.__dict__[key], MutableSet) for key in immutable_keys)):
            self.__init__(
                terminals=frozenset(self.terminals),
                nonterminals=frozenset(self.nonterminals),
                starting_symbol=self.starting_symbol,
                productions=frozenset(self.productions)
            )

    @classmethod
    def from_dict(cls: type[SelfData], grammar_dict: dict) -> SelfData:
        """Create new GrammarData from dict"""
        return cls(**grammar_dict)

    @classmethod
    def from_str(cls: type[SelfData], grammar_str: str) -> SelfData:
        """Create new GrammarData from string"""
        return cls.from_dict(parse(grammar_str))

    def to_dict(self) -> dict:
        """Create mutable descriptive dict from GrammarData

        Unfreeze the sets in progress
        """
        return {
            "terminals": set(self.terminals),
            "nonterminals": set(self.nonterminals),
            "starting_symbol": self.starting_symbol,
            "productions": set(self.productions)
        }

    def to_correct_chomsky_hierarchy_level(self) -> Union[Grammar, MonotoneGrammar, ContextFreeGrammar, RegularGrammar]:
        """Return a new object of appropriate class corresponding to chomsky type

        :return:
        """
        chomsky_type = self.get_chomsky_type()
        if chomsky_type == ChomskyType.UNRESTRICTED:
            return Grammar.from_dict(self.__dict__)
        elif chomsky_type == ChomskyType.MONOTONE:
            return MonotoneGrammar.from_dict(self.__dict__)
        elif chomsky_type == ChomskyType.CONTEXT_FREE:
            return ContextFreeGrammar.from_dict(self.__dict__)
        elif chomsky_type == ChomskyType.REGULAR:
            return RegularGrammar.from_dict(self.__dict__)
        else:
            raise RuntimeError(f"Unexpected return of "
                               f":py:function:`formgram.grammars.classifiers.chomsky_classifiers.get_chomsky_type`"
                               f": {chomsky_type}")

    def get_chomsky_type(self) -> ChomskyType:
        """Get chomsky type of grammar

        :return:
        """
        return get_chomsky_type(self.to_dict())

    def __str__(self) -> str:
        return to_backus_naur_form(self.to_dict())

    def __repr__(self) -> str:
        return self.to_dict().__repr__()


class Grammar(GrammarData):
    """Type 0 or unrestricted Grammar

    """

    @classmethod
    def from_turing_machine(cls: type[SelfGrammar], machine: TuringMachine) -> SelfGrammar:
        """Takes TuringMachine Object and creates Grammar

        :param machine:
        :return:
        """
        return cls.from_dict(turing_interface.to_grammar(machine.to_dict()))

    def generate_words_in_limited_steps(self, fuel: int = 100) -> Set[Tuple[str]]:
        """Generate the set of all words generatable in `fuel` steps

        :param fuel:
        :return:
        """
        return generate_words_in_limited_steps(grammar=self.to_dict(), fuel=fuel)


class MonotoneGrammar(Grammar):
    """Type 1 Grammar

    """
    def to_context_sensitive_form(self) -> MonotoneGrammar:
        """Create equivalent context sensitive grammar

        :return:
        """
        return MonotoneGrammar(**to_context_sensitive_form(self.to_dict()))

    def generate_words_limited_by_length(self, length: int) -> Set[Tuple[str]]:
        """Generate the set of all generatable words shorter or equal to length

        :param length:
        :return:
        """
        return generate_words_limited_by_length(grammar=self.to_dict(), max_length=length)


class ContextFreeGrammar(MonotoneGrammar):
    """Type 2 Grammar

    """
    def to_chomsky_normal_form(self) -> ContextFreeGrammar:
        """Create equivalent grammar in Chomsky normal form

        :return:
        """
        return ContextFreeGrammar(**to_chomsky_normal_form(self.to_dict()))

    def to_greibach_normal_form(self) -> ContextFreeGrammar:
        """Create equivalent grammar in Greibach normal form

        :return:
        """
        return ContextFreeGrammar(**to_greibach_normal_form(self.to_dict()))

    @staticmethod
    def from_pushdown_automaton(machine: PushdownAutomaton) -> ContextFreeGrammar:
        """Create context free grammar from PushdownAutomaton

        :param machine:
        :return:
        """
        return ContextFreeGrammar.from_dict(to_context_free_grammar(machine.to_dict()))


class RegularGrammar(ContextFreeGrammar):
    """Type 3 Grammar

    This includes extended regular grammars. Those allow more than one terminal
    per production, as long as all nonterminals are still on the same end of the
    right hand sides.
    """

    @staticmethod
    def from_finite_automaton(machine: FiniteAutomaton) -> RegularGrammar:
        """Initialize from FiniteAutomaton

        :param machine:
        :return:
        """
        return RegularGrammar.from_dict(to_right_regular_grammar(machine))

    def to_left_linear_form(self) -> RegularGrammar:
        """Create equivalent grammar in left linear form

        :return:
        """
        return RegularGrammar(**to_left_linear_form(self.to_dict()))

    def to_right_linear_form(self) -> RegularGrammar:
        """Create equivalent grammar in right linear form

        :return:
        """
        return RegularGrammar(**to_right_linear_form(self.to_dict()))

    def to_left_regular_form(self) -> RegularGrammar:
        """Create equivalent grammar in left regular form

        :return:
        """
        return RegularGrammar(**to_left_regular_form(self.to_dict()))

    def to_right_regular_form(self) -> RegularGrammar:
        """Create equivalent grammar in right regular form

        :return:
        """
        return RegularGrammar(**to_right_regular_form(self.to_dict()))
