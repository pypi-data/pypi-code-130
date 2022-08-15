"""Main library."""
from .Base import Base
from .VerifyAction import VerifyAction as Vfy


class RobotEditSuperFastLib(Base, Vfy):
    @staticmethod
    def hi(name):
        print(f"hi, {name}")
