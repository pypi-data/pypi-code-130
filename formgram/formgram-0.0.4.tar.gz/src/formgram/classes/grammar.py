"""This module provides grammar classes for easy usage.

The classes are structured hierarchical, as to only show methods which can be
used on the given Chomsky hierarchy level.

.. warning::
    The classes themself do NOT check if the provided grammar is of correct
    type. One can initialize a :class:`MonotoneGrammar` with non-monotone
    transitions. Note that in this case the methods are not guaranteed to work.

.. note::
    Due to not checking correctness of hierarchy level, it is highly suggested
    to initialize via :class:`UnrestrictedGrammar` and use
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
from formgram.grammars.types import Alphabet, Symbol, Production, GrammarDict
from formgram.grammars.utility.monotone.generator import generate_words_limited_by_length
from formgram.grammars.utility.unrestricted.generator import generate_words_in_limited_steps
from formgram.grammars.utility.unrestricted.helper import to_backus_naur_form
from formgram.machines.finite_automata.grammar_interface import to_right_regular_grammar
from formgram.machines.pushdown_automata.grammar_interface import to_context_free_grammar
import formgram.machines.turing_machines.grammar_interface as turing_interface

# In Python 3.11 one would use Self from typing_extensions
# This is the previous correct version as described in PEP 673

SelfData = TypeVar("SelfData", bound="GrammarData")
SelfGrammar = TypeVar("SelfGrammar", bound="UnrestrictedGrammar")


@dataclass(frozen=True)
class GrammarData:
    """Container for all internal values for any grammar

    This is frozen, so that attributes can't be changed after creation.

    .. warning:
        Types are not checked at creation. Thus if sets are supplied instead
        of frozensets, the attributes are still mutable.
    """
    terminals: frozenset[str]
    nonterminals: frozenset[str]
    starting_symbol: str
    productions: frozenset[tuple[str]]


class Grammar(GrammarData):
    """Extending GrammarData with functionality for creating on different levels

    """

    def __new__(cls,
                terminals: Alphabet,
                nonterminals: Alphabet,
                starting_symbol: Symbol,
                productions: Set[Production]) -> Grammar:
        """Overwrite the constructor to create the correct chomsky level

        :param terminals:
        :param nonterminals:
        :param starting_symbol:
        :param productions:
        :return: A Grammar subclass object of maximal allowed chomsky hierarchy
            level
        """

        # if the request came from a subclass just transfer it.
        if cls != Grammar:
            return GrammarData.__new__(cls)

        # otherwise determine correct level and use that level

        grammar_dict: GrammarDict = {
            "terminals": terminals,
            "nonterminals": nonterminals,
            "starting_symbol": starting_symbol,
            "productions": productions
        }
        validate_grammar_form(grammar_dict)
        chomsky_type = get_chomsky_type(grammar_dict)
        if chomsky_type == ChomskyType.REGULAR:
            correct_class = RegularGrammar
        elif chomsky_type == ChomskyType.CONTEXT_FREE:
            correct_class = ContextFreeGrammar
        elif chomsky_type == ChomskyType.MONOTONE:
            correct_class = MonotoneGrammar
        else:
            correct_class = UnrestrictedGrammar

        return GrammarData.__new__(correct_class)

    def __init__(self,
                 terminals: Alphabet,
                 nonterminals: Alphabet,
                 starting_symbol: Symbol,
                 productions: Set[Production]):
        """Freeze all sets before initializing

        :param terminals:
        :param nonterminals:
        :param starting_symbol:
        :param productions:
        """
        if isinstance(terminals, MutableSet):
            terminals = frozenset(terminals)
        if isinstance(nonterminals, MutableSet):
            nonterminals = frozenset(nonterminals)
        if isinstance(productions, MutableSet):
            productions = frozenset(productions)
        super().__init__(terminals, nonterminals, starting_symbol, productions)

    @classmethod
    def from_dict(cls: type[SelfData], grammar_dict: GrammarDict) -> SelfData:
        """Create new GrammarData from dict

        :param grammar_dict:
        :return: new grammar object
        """
        return cls(**grammar_dict)

    @classmethod
    def from_str(cls: type[SelfData], grammar_str: str) -> SelfData:
        """Create new GrammarData from string

        :param grammar_str:
        :return: new gramamr object
        """
        return cls.from_dict(parse(grammar_str))

    def to_dict(self) -> GrammarDict:
        """Create mutable descriptive dict from GrammarData

        Unfreeze the sets in progress

        :return: dictionary as described in package init
        """
        return {
            "terminals": set(self.terminals),
            "nonterminals": set(self.nonterminals),
            "starting_symbol": self.starting_symbol,
            "productions": set(self.productions)
        }

    def to_correct_chomsky_hierarchy_level(self) -> Union[UnrestrictedGrammar,
                                                          MonotoneGrammar,
                                                          ContextFreeGrammar,
                                                          RegularGrammar]:
        """Return a new object of appropriate class corresponding to chomsky type

        :return: Grammar subclass object of maximal chomsky type
        """
        chomsky_type = self.get_chomsky_type()
        if chomsky_type == ChomskyType.UNRESTRICTED:
            return UnrestrictedGrammar.from_dict(self.__dict__)
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

        :return: ChomskyType of given grammar
        """
        return get_chomsky_type(self.to_dict())

    def __str__(self) -> str:
        """Create extended Backus Naur form string from grammar

        :return: Backus Naur form of grammar
        """
        return to_backus_naur_form(self.to_dict())

    def __repr__(self) -> str:
        """Create a dictionary representation of this grammar

        :return: dictionary representation of grammar
        """
        return self.to_dict().__repr__()


class UnrestrictedGrammar(Grammar):
    """Type 0 or unrestricted grammar

    """

    @classmethod
    def from_turing_machine(cls: type[SelfGrammar], machine: TuringMachine) -> SelfGrammar:
        """Takes TuringMachine object and creates grammar

        :param machine:
        :return: new UnrestrictedGrammar
        """
        return cls.from_dict(turing_interface.to_grammar(machine.to_dict()))

    def generate_words_in_limited_steps(self, steps: int = 100) -> Set[Tuple[Symbol]]:
        """Generate the set of all words generatable in limited steps

        :param steps:
        :return: set of creatable words
        """
        return generate_words_in_limited_steps(grammar=self.to_dict(), steps=steps)


class MonotoneGrammar(UnrestrictedGrammar):
    """Type 1 grammar

    """
    def to_context_sensitive_form(self) -> MonotoneGrammar:
        """Create equivalent context sensitive grammar

        :return: new grammar object of context sensitive form
        """
        return MonotoneGrammar(**to_context_sensitive_form(self.to_dict()))

    def generate_words_limited_by_length(self, length: int) -> Set[Tuple[Symbol]]:
        """Generate the set of all generatable words shorter or equal to length

        :param length:
        :return: set of creatable words
        """
        return generate_words_limited_by_length(grammar=self.to_dict(), max_length=length)


class ContextFreeGrammar(MonotoneGrammar):
    """Type 2 grammar

    """
    def to_chomsky_normal_form(self) -> ContextFreeGrammar:
        """Create equivalent grammar in Chomsky normal form

        :return: new grammar object of Chomsky normal form
        """
        return ContextFreeGrammar(**to_chomsky_normal_form(self.to_dict()))

    def to_greibach_normal_form(self) -> ContextFreeGrammar:
        """Create equivalent grammar in Greibach normal form

        :return: new grammar object of Greibach normal form
        """
        return ContextFreeGrammar(**to_greibach_normal_form(self.to_dict()))

    @staticmethod
    def from_pushdown_automaton(machine: PushdownAutomaton) -> ContextFreeGrammar:
        """Create context free grammar from PushdownAutomaton

        :param machine:
        :return: new grammar object
        """
        return ContextFreeGrammar.from_dict(to_context_free_grammar(machine.to_dict()))


class RegularGrammar(ContextFreeGrammar):
    """Type 3 grammar

    This includes extended regular grammars. Those allow more than one terminal
    per production, as long as all nonterminals are still on the same end of the
    right hand sides.
    """

    @staticmethod
    def from_finite_automaton(machine: FiniteAutomaton) -> RegularGrammar:
        """Initialize from FiniteAutomaton

        :param machine:
        :return: new grammar object
        """
        return RegularGrammar.from_dict(to_right_regular_grammar(machine))

    def to_left_linear_form(self) -> RegularGrammar:
        """Create equivalent grammar in left linear form

        :return: new grammar object of left linear form
        """
        return RegularGrammar(**to_left_linear_form(self.to_dict()))

    def to_right_linear_form(self) -> RegularGrammar:
        """Create equivalent grammar in right linear form

        :return: new grammar object of right linear form
        """
        return RegularGrammar(**to_right_linear_form(self.to_dict()))

    def to_left_regular_form(self) -> RegularGrammar:
        """Create equivalent grammar in left regular form

        :return: new grammar object of left regular form
        """
        return RegularGrammar(**to_left_regular_form(self.to_dict()))

    def to_right_regular_form(self) -> RegularGrammar:
        """Create equivalent grammar in right regular form

        :return: new grammar object of right regular form
        """
        return RegularGrammar(**to_right_regular_form(self.to_dict()))
