"""
Errors used in all modules of compressed_filepath
"""
from .tokenize import TokenParseError


class IterationPaddingMisMatch(ValueError):
    """
    If the padding of a IterationSet is set and the Iteration being added does not match
    """
    
    
class IterationSetParseError(Exception):
    """
    Unable to convert a formatted string to IterationSet
    """


class MergeError(Exception):
    """
    When objects of 2 different types can't merge or when 2 partitioned filepaths cannot merge
    """


class StringReprFormatError(KeyError):
    """
    When you run str_repr on a compressed filepath type but,
    the defined format template is unable to be fufilled by
    the tokens parsed from the filepath.
    """


class FilesNotLocal(Exception):
    """
    Unable to find files on disk to assist with created a CompressedFilepath
    """
