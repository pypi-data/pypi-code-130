"""This library provides code to learn, teach and/or explore formal languages.

-----------------
Usage of Packages
-----------------

The centerpiece of this library is the :py:mod:`grammars <formgram.grammars>`
package. It contains the grammar algorithms, which this library wishes to
provide and convey.
It is encouraged to study the source code of this package.

The :py:mod:`machines <formgram.machines>` package exists to show
the relationship between automata and grammars.
The source code shows algorithms to transform grammars into automata and vice
versa and is thusly also encouraged to be studied.

Lastly the :py:mod:`classes <formgram.classes>` package provides a way to
explore the previous two packages in a close to object-oriented way.

.. note::
    To provide a cleaner import statement, formgram exports the most important
    classes from the :py:mod:`classes <formgram.classes>` package:

    * :py:class:`Grammar <formgram.classes.grammar.Grammar>`.
    * :py:class:`FiniteAutomaton <formgram.classes.finite_automaton.FiniteAutomaton>`.
    * :py:class:`PushdownAutomaton <formgram.classes.pushdown_automaton.PushdownAutomaton>`.
    * :py:class:`TuringMachine <formgram.classes.turing_machine.TuringMachine>`.


-------------
Usage Example
-------------

>>> from formgram import Grammar
>>> grammar = Grammar.from_str('''<S> ::= 'a' <S> |''').to_correct_chomsky_hierarchy_level()
>>> grammar.get_chomsky_type()
<ChomskyType.Regular: 3>
>>> from formgram import FiniteAutomaton
>>> finite_automaton = FiniteAutomaton.from_grammar(grammar)
>>> finite_automaton.does_accept("aaaa")
True
>>> finite_automaton.does_accept("aab")
False

"""

from formgram.classes.grammar import Grammar
from formgram.classes.turing_machine import TuringMachine
from formgram.classes.finite_automaton import FiniteAutomaton
from formgram.classes.pushdown_automaton import PushdownAutomaton
