from abc import ABC
from abc import abstractmethod
from typing import List
from naveen.experiment.config.abstract_config import AbstractConfig  # type: ignore # noqa: E501


class Experiment(ABC):

    def __init__(self, config: AbstractConfig):
        self.config = config

    @abstractmethod
    def get_results(self) -> List[dict]:
        pass


class DemoExperiment(Experiment):
    # don't change this class of ir messes up tests
    def get_results(self) -> List[dict]:
        return [{"prod": "az", "hedonic": 8, "utilitatian": 9},
                {"prod": "aa", "hedonic": 9, "utilitatian": 9}]
