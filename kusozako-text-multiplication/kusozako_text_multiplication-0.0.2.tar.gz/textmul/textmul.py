import typing


class TextMul(str):
    def __new__(cls, val: str):
        if type(val) is not str:
            raise ValueError("A non-string has been entered.")
        return super().__new__(cls, val)

    def __mul__(self, value: typing.Union[str, int]) -> str:
        if type(value) is int:
            return TextMul(str(self) * value)
        tmp = self
        result = ""
        for v in list(tmp):
            for v2 in list(value):
                result += v + v2
        return TextMul(result)

    def __pow__(self, value: int) -> str:
        if type(value) is not int:
            raise ValueError("Not a number.")
        elif value <= 0:
            raise ValueError("You have not entered a valid number.")

        if value == 1:
            return self
        return TextMul.__pow__(self * self, value=value - 1)
