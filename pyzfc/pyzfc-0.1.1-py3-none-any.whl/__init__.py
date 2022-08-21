"""
(ZFC) set-theoretic definition of natural numbers.

0 is defined as the empty set ``{}``,
and the rest of the natural numbers
are defined recursively as ``n + 1 = n ∪ {n}``.
"""

from .zfc import NaturalNumber

__author__ = "Yuanhao 'Nyoeghau' Chen"
__license__ = "MIT"
__version__ = "0.1.1"
__email__ = "nyoeghau@nyoeghau.com"

__all__ = ["NaturalNumber"]
