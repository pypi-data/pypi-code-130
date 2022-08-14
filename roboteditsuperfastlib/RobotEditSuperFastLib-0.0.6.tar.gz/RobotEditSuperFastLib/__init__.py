"""Main library."""
from .Base import Base
from .VerifyAction import VerifyAction as Vfy


class RobotEditSuperFastLib(Base, Vfy):
    @staticmethod
    def hi(name):
        print(f"hi, {name}")

    @staticmethod
    def to_json(dict_data: dict):
        return dict_data
