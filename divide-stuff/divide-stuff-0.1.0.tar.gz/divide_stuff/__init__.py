__version__ = "0.1.0"

from pprintpp import pprint as pp


class Divider:
    """
    Amazing class that can divide two numbers.
    """

    def divide_numbers(self, a: int, b: int) -> float:
        return a / b

    def divide_numbers_print(self, a: int, b: int) -> None:
        pp({"result": a / b})
