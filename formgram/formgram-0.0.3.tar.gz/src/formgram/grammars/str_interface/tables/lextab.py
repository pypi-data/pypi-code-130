


# lextab.py. This file automatically created by PLY (version 3.11). Don't edit!
_tabversion = "3.10"
_lextokens = set(("ARROW", "NEWLINE", "NONTERMINAL", "OR", "TERMINAL"))
_lexreflags = 64
_lexliterals = ""
_lexstateinfo = {"INITIAL": "inclusive"}
_lexstatere = {
    "INITIAL": [
        (
            "(?P<t_NEWLINE>\\n+)|(?P<t_NONTERMINAL><(?:[^\\\\<>\\'\\\"]|\\\\<|\\\\>|\\\\\\\\|\\\\\\'|\\\\\\\")+>)|(?P<t_TERMINAL>['\\\"](?:[^\\\\<>\\'\\\"]|\\\\<|\\\\>|\\\\\\\\|\\\\\\'|\\\\\\\")+['\\\"])|(?P<t_ignore_COMMENT>\\#.*)|(?P<t_ARROW>::=)|(?P<t_OR>\\|)",
            [
                None,
                ("t_NEWLINE", "NEWLINE"),
                ("t_NONTERMINAL", "NONTERMINAL"),
                ("t_TERMINAL", "TERMINAL"),
                (None, None),
                (None, "ARROW"),
                (None, "OR"),
            ],
        )
    ]
}
_lexstateignore = {"INITIAL": " \t\r"}
_lexstateerrorf = {"INITIAL": "t_error"}
_lexstateeoff = {"INITIAL": "t_eof"}
