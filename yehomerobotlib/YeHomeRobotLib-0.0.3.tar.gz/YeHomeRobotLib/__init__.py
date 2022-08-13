"""Main library."""
from A import A
from B import B

__version__ = "0.0.1"


class YeHomeRobotLib(
    A, B
):
    @staticmethod
    def hi(name):
        print(f"hi, {name}")

    @staticmethod
    def to_json(dict_data: dict):
        return dict_data


