from YeHomeRobotLib import YeHomeRobotLib
from B import B


class A:
    @staticmethod
    def learn(context):
        print(f"learn, {context}")


class All(YeHomeRobotLib, A, B):
    @staticmethod
    def hello(name):
        print(f"hello, {name}")



