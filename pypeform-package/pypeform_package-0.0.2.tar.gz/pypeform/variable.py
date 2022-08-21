import typing


class Variable:
    key: str
    type: str
    value: typing.Union[str, float, int]

    def __init__(self, key: str, _type: str, value: typing.Union[str, float, int]):
        self.key = key
        self.type = _type
        self.value = value

    def __repr__(self):
        return f'Variable(key: {self.key}, type: {self.type}, value: {self.value})'

    def __str__(self):
        return self.__repr__()
