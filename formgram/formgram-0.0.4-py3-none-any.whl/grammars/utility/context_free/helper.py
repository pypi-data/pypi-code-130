"""
TODO write docu
"""
from typing import Set


def collect_nullable_symbols(grammar: dict) -> Set[str]:
    """Return the subset of nonterminals which can produce the empty word

     This function iterates over the collection of productions collecting all
     nonterminals which can directly produce the empty word.
     This collection of nullable nonterminals is then expanded each iteration by
     all nonterminals which can directly produce any word of only nullable symbols.
     The iterations continue until no new nonterminals are found.

    :examples:
        >>> grammar_string = '''
        >>> <S> ::= <A> <A> <A> | <A> <B> <A> |
        >>> <A> ::=
        >>> <B> ::= 'b'
        >>> '''
        >>> from formgram.grammars.str_interface import parse
        >>> grammar = parse(grammar_string)
        >>> collect_nullable_symbols(grammar)
        {"S", "A"}

    :param grammar: The grammar to collect nullable nonterminals of
    :return: The set of nullable nonterminals
    """
    nullable_symbols: Set[str] = set()
    while True:
        newly_found_nullable_symbols = set()
        for (non_terminal,), right_hand_side in grammar["productions"]:
            if non_terminal not in nullable_symbols and nullable_symbols.issuperset(
                right_hand_side
            ):
                newly_found_nullable_symbols.add(non_terminal)
        nullable_symbols.update(newly_found_nullable_symbols)
        if not newly_found_nullable_symbols:
            return nullable_symbols
