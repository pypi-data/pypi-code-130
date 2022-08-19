from typing import Dict, Protocol

from ..utils import Classify, dict_zip_data, list_of_dict
from .__SectionDict import __SectionDict


class MsrRecordDict(__SectionDict):
    """
    MsrRecordDict A MsrRecord string is converted to a Dict.

    Args:
        MsrDict (Protocol): Basic representation of Msr rows as Dict.

    Raises:
        KeyError: The String was not passed with the desired key.
    """

    __keys: list[str] = ["ID", "NA", "MP", "LB", "MT", "ST", "LT", "NI1", "AD", "SB", "NI2", "NI3", "NI4", "NI5"]

    def merge_dict(self, splitted_list: list[str]) -> Dict:
        """
        merge_dict Merge data for Dataprocessing.

        Returns:
            Dict: A MsrDict separated by the predefined separator
        """
        data_as_dict = {}
        classify = Classify(splitted_list)
        return data_as_dict | classify.execute(dict_zip_data(self.__keys))


class UidAccDict(__SectionDict):
    """
    UidAccDict A UidAcc string is converted to a Dict.
    Args:
        MsrDict (Protocol): Basic representation of Msr rows as Dict.
    Raises:
        KeyError: The String was not passed with the desired key.
    """
    __keys: list[str] = ["USER", "ACC"]
    __secondary_dict_len: int = 2

    def merge_dict(self, splitted_list: list[str]) -> Dict:
        """
        merge_dict Merge data for Dataprocessing.
        Returns:
            Dict: A MsrDict separated by the predefined separator
        """
        data_as_dict = {}
        data_as_dict["ID"], data_as_dict["LEN"], *parameter = splitted_list
        classify = Classify(parameter)
        data_as_dict["PARA"] = classify.execute(list_of_dict(self.__keys, self.__secondary_dict_len))
        return data_as_dict
