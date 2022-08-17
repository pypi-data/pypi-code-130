from modelfun.response import ModelfunObject
from typing import List


class Tokens(ModelfunObject):
    def __init__(self, tokens: List[int]) -> None:
        self.tokens = tokens
        self.iterator = iter(tokens)
        self.length = len(tokens)

    def __iter__(self) -> iter:
        return self.iterator

    def __next__(self) -> next:
        return next(self.iterator)

    def __len__(self) -> int:
        return self.length
