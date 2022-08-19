from typing import Dict

from ..utils import Classify, list_of_dict
from .__SectionDict import __SectionDict


class GwyDict(__SectionDict):
    """
    GwyDict A Gwy([GWY:ACCMSR] or [GWY:ACCEAM]) string is converted to a Dict.
    Args:
        MsrDict (Protocol): Basic representation of Msr rows as Dict.
    Raises:
        KeyError: The String was not passed with the desired key.
    """
    __keys: list[str] = ["GN", "G1", "G2"]
    __secondary_dict_len: int = 3

    def merge_dict(self, splitted_data: list[str]) -> Dict:
        """
        merge_dict Merge data for Dataprocessing.
        Returns:
            Dict: A MsrDict separated by the predefined separator
        """
        data_as_dict = {}
        data_as_dict["ID"], data_as_dict["MP"], data_as_dict["LEN"], *parameter = splitted_data
        classify = Classify(parameter[:-1])
        data_as_dict["PARA"] = classify.execute(list_of_dict(self.__keys, self.__secondary_dict_len))
        return data_as_dict | {"END": parameter[-1]}
