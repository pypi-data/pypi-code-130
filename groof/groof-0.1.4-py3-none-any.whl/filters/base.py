from dataclasses import dataclass
from abc import ABC


@dataclass
class Filter(ABC):
    def __call__(self):
        """ Check update from context """
