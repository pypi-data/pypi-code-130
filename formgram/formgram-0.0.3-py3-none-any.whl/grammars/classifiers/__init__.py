"""This subpackage provides various modules to gain information about grammars

It features multiple modules:

#. :mod:`classes.classifers.chomsky_classifiers`
    Featuring functions of the format ``is_<X>`` and importantly :func:`get_chomsky_type`
#. :mod:`classes.classifers.form_classifiers`
    Featuring functions of the format ``has_<X>_form``

:example:
    >>> from formgram.grammars.str_interface import parse
    >>> from formgram.grammars.classifiers.chomsky_classifiers import get_chomsky_type
    >>> from formgram.grammars.classifiers.form_classifiers import has_chomsky_normal_form
    >>> grammar_text = '''<S> ::= <S> <S> | "s"'''
    >>> grammar_dict = parse(grammar_text)
    >>> get_chomsky_type(grammar_dict)
    <ChomskyType.CONTEXT_FREE: 2>
    >>> has_chomsky_normal_form(grammar_dict)
    True
"""
