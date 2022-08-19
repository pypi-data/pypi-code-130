from abc import ABC, abstractclassmethod
from typing import Dict


class __SectionDict(ABC):

    @abstractclassmethod
    def merge_dict(self, splitted_data: list[str]) -> Dict[str, str] | Dict[str, list]:
        """
        merge data to dict. 
        """
