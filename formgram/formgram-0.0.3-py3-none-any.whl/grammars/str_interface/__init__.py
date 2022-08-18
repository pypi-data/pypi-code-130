"""This package uses yacc to parse strings into grammar dicts

:example:
    >>> grammar_string = ''' # comments look like this and are permitted in the string
    >>> <START> ::= <A> | 's' <START>
    >>> 's''s'<A> ::= 's'<A>'s'
    >>> <A> ::= <START> <START>
    >>> 's'<A>'s' ::= 'a'
    >>> <A> ::=  # this is an epsilon rule
    >>> '''
    >>> grammar = parse(grammar_string)
    >>> grammar
    {
        "terminals": {"s", "a"},
        "nonterminals": {"START", "A"},
        "productions": {
            (("START", ), ("A", )),
            (("START", ), ("s", "START")),
            (("s", "s", "A"), ("s", "A", "s")),
            (("A", ), ("START", "START")),
            (("s", "A", "s"), ("a", )),
            (("A", ), ())
        },
        "starting_symbol": "START"
    }
"""


from formgram.grammars.str_interface.backus_naur_parser import parse
