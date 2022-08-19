from typing import Dict, Protocol

from ..utils import Classify, dict_zip_data, list_of_dict
from .__SectionDict import __SectionDict


class ParaDataDict(__SectionDict):
    """
    ParaDataDict A ParaData string is converted to a Dict.
    Args:
        MsrDict (Protocol): Basic representation of Msr rows as Dict.
    Raises:
        KeyError: The String was not passed with the desired key.
    """
    __keys: list[str] = ["KN", "L1", "K1", "L2", "K2"]
    __secondary_dict_len: int = 5

    def merge_dict(self, splitted_data: list[str]) -> Dict:
        """
        merge_dict Merge data for Dataprocessing.
        Returns:
            Dict: A MsrDict separated by the predefined separator
        """
        data_as_dict = {}
        data_as_dict["ID"], data_as_dict["LEN"], *parameter = splitted_data
        classify = Classify(parameter)
        data_as_dict["PARA"] = classify.execute(list_of_dict(self.__keys, self.__secondary_dict_len))
        print(data_as_dict["PARA"])
        return data_as_dict
