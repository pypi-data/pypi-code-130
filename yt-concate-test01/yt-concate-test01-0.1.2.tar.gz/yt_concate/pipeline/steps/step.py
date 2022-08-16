from abc import ABC
from abc import abstractmethod


class Step(ABC):
    def __int__(self):
        pass

    @abstractmethod
    def process(self, data, inputs, utils):
        pass


class StepException(Exception):
    pass
