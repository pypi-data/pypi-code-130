


"""This package provides functions to analyze and work with grammars of formal languages.

.. _grammar description:

It has a number of subpackages organizing those functions into loose categories.


Subpackage Description
======================

#. classifiers
    which provides functions which can be used to analyze grammars
#. str_interface
    which provides a single function to import grammars from a string
#. helper_functions
    which provides needed functions to other subpackages, which don't directly have anything to do with formal grammars
#. transformations
    which provides functions to turn grammars into grammars of other forms


Grammar definition
==================

The grammar object which is used anywhere else in this code is a :class:`dict` with keys

* "terminals"
    a :class:`set` of :class:`str` disjoint with nonterminals
* "nonterminals"
    a :class:`set` of :class:`str` disjoint with terminals
* "productions"
    a :class:`set` of production :class:`tuple`, each consisting of two :class:`tuple` consisting of entries of the
    terminals or nonterminals set.
    ``{(('S',), ('a',)), (('S',), ('a', 'S'))}``
* "starting_symbol"
    a :class:`str` from the nonterminals set

The
:py:mod:`str_interface <formgram.grammars.str_interface>`
subpackage provides
:py:func:`parse <formgram.grammars.str_interface.backus_naur_parser.parse>`
which takes a string formatted in a variant of the
`Backus-Naur Form <https://en.wikipedia.org/wiki/Backus%E2%80%93Naur_form>`__
extended to allow arbitrary words on the left hand side of ``::=``.

:example:
    >>> from formgram.grammars.str_interface import parse
    >>> from formgram.grammars.classifiers.chomsky_classifiers import get_chomsky_type
    >>> grammar_string = ''' <S> ::= 'a' <S> | <S> <S>
    >>> 'a' <S> ::= 'a'
    >>> '''
    >>> grammar_dict = parse(grammar_string)
    >>> get_chomsky_type(grammar_dict)
    <ChomskyType.UNRESTRICTED: 0>
"""
