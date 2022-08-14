import abc
from typing import List

__all__ = [
    "Iter",
    "PrefixChecker",
    "splitargs",
]


def splitargs(text: str) -> List[str]:
    """splits string by space and quotes.

    Parameters
    ----------
    text : str
        The string to split.
    """
    result: List[str] = []

    in_quote: bool = False
    quote: str = ""
    segment: str = ""

    for char in text:
        if not in_quote:
            if char == " " and segment:
                result.append(segment)
                segment = ""
            elif char in "'\"":
                quote = char
                in_quote = True
            else:
                segment += char
        else:
            if char == quote and segment:
                result.append(segment)
                segment = ""
            else:
                segment += char

    if segment:
        result.append(segment)

    return result


class Iter(abc.ABC):
    """base string iterator class.

    Parameters
    ----------
    text : str
        The string to iterate.
    """

    def __init__(self, text: str):
        self.text = text

        self._index = -1
        self._char = None

        self._start()

    def _next(self):
        self._index += 1

        if self._index < len(self.text):
            self._char = self.text[self._index]
        else:
            self._char = None

    @abc.abstractmethod
    def _start(self):
        self._next()  # start at index 0

        while self._char is not None:
            self._next()


class PrefixChecker(Iter):
    """Checks if prefix is valid.

    Parameters
    ----------
    text : str
        The string to check
    prefix : str
        The prefix.
    """

    is_valid: bool

    def __init__(self, text: str, prefix: str):
        self.prefix = prefix
        self.is_valid = False
        super().__init__(text=text)

    @property
    def strip_prefix(self):
        """removes prefix from the original string."""
        if self.is_valid:
            return self.text[self._index :].lstrip()

    def _start(self):
        self._next()

        space_count = 0

        while self._char is not None:
            if self._char != " ":
                prefix = self.text[: self._index].rstrip()

                if prefix == self.prefix and space_count < 2:
                    self.is_valid = True
                    break
            else:
                space_count += 1

            self._next()
