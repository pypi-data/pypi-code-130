from typing import Dict

from ..utils import Classify, dict_zip_data
from .__SectionDict import __SectionDict


class EamRecordDict(__SectionDict):
    """
    EamRecordDict A EamRecord string is converted to a Dict.
    Args:
        MsrDict (Protocol): Basic representation of Msr rows as Dict.
    Raises:
        KeyError: The String was not passed with the desired key.
    """

    __keys: list[str] = ["ID", "NA", "VN", "NI1", "DT", "VT", "PI", 'EX']

    def merge_dict(self, splitted_data: list[str]) -> Dict:
        """
        merge_dict Merge data for Dataprocessing.
        Returns:
            Dict: A MsrDict separated by the predefined separator
        """
        data_as_dict = {}
        classify = Classify(splitted_data)
        return data_as_dict | classify.execute(dict_zip_data(self.__keys))
