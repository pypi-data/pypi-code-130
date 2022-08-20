"""This module provides type aliases for function annotations

"""

from typing import Tuple, Set, Dict, Union

Symbol = str
Side = Tuple[Symbol, ...]
Production = Tuple[Side, Side]
Alphabet = Set[Symbol]
GrammarDict = Dict[str, Union[Symbol, Production, Alphabet]]
