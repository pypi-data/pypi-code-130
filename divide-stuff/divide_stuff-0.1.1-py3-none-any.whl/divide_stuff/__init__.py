"""
Module Divide Stuff. An amazing project to help you divide stuff.
"""

__version__ = "0.1.1"

from pprintpp import pprint as pp


class Divider:
    """
    Amazing class that can divide two numbers.
    """

    def divide_numbers(self, num_1: int, num_2: int) -> float:
        """
        Takes two numbers and returns the divided number.
        """
        return num_1 / num_2

    def divide_numbers_print(self, num_1: int, num_2: int) -> None:
        """
        Takes two numbers and prints the divided number.
        """
        pp({"result": num_1 / num_2})
