from typing import Dict

from ..utils import Classify, dict_zip_data
from .__SectionDict import __SectionDict


class AreaDict(__SectionDict):
    """
    AreaDict A Area string is converted to a Dict.
    """

    __keys: list[str] = ["ID", "NA", "AC", "LA", "AN"]

    def merge_dict(self, splitted_data: tuple[str]) -> Dict[str, str]:
        """
        merge_dict Merge data for Dataprocessing.
        Returns:
            Dict: A ProjectDict separated by the predefined separator
        """
        data_as_dict = {}
        classify = Classify(splitted_data)
        return data_as_dict | classify.execute(dict_zip_data(self.__keys))
