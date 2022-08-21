import datetime
import typing

from .field import Field


class Answer:
    answer: typing.Union[typing.List[str], int, float, str]
    full_type: str
    reference: str
    simple_type: str
    field: Field

    def __init__(self, answer: typing.Union[typing.List[str], int, float, str, datetime.datetime], full_type: str,
                 reference: str, simple_type: str):
        self.answer = answer
        self.full_type = full_type
        self.reference = reference
        self.simple_type = simple_type

    def __repr__(self):
        return f'Answer(ref: {self.reference}, full type: {self.full_type}, ' \
               f'simple type: {self.simple_type}, answer: {self.answer})'

    def __str__(self):
        return self.__repr__()
