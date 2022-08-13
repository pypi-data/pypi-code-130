from HjyRobotLib import HjyRobotLib
from B import B


class A:
    @staticmethod
    def learn(context):
        print(f"learn, {context}")


class All(HjyRobotLib, A, B):
    @staticmethod
    def hello(name):
        print(f"hello, {name}")



