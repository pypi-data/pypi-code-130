"""Top-level package for interval_search."""

__author__ = """Matthew Andres Moreno"""
__email__ = 'm.more500@gmail.com'
__version__ = '0.2.0'

from .binary_search import binary_search
from .doubling_search import doubling_search
from .interval_search import interval_search

# adapted from https://stackoverflow.com/a/31079085
__all__ = [
    'binary_search',
    'doubling_search',
    'interval_search',
]
