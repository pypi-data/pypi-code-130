from typing import Dict, Tuple

from ..utils import Classify, dict_zip_data, tuple_of_decode_ascii_code
from .__SectionDict import __SectionDict


class Hw2BlobDict(__SectionDict):
    """
    Hw2BlobDict A Hw2Blob string is converted to a Dict.
    Args:
        HwmDict (Protocol): Basic representation of Hwm rows as Dict.
    Raises:
        KeyError: The String was not passed with the desired key.
    """
    __keys: list[str] = ["ID", "DTMN", "QC"]

    def merge_dict(self, splitted_data: list[str]) -> Dict:
        """
        merge_dict Merge data for Dataprocessing. Includes Ascii encoding.
        Returns:
            Dict: A HwmDict separated by the predefined separator
        """
        classify_ascii = Classify(splitted_data[-1])
        classify = Classify(splitted_data[:-1])
        decoded: Dict[Tuple] = classify_ascii.execute(tuple_of_decode_ascii_code("DTMC", int(splitted_data[2])))
        return classify.execute((dict_zip_data(self.__keys))) | decoded


class BeginIODescriptionDict(__SectionDict):
    """
    BeginIODescriptionDict A BeginIODescription string is converted to a Dict.
    Args:
        HwmDict (Protocol): Basic representation of Hwm rows as Dict.
    Raises:
        KeyError: The String was not passed with the desired key.
    """

    __keys: list[str] = [
        "ID", "CN", "IO", "DT", "UB", "B", "BL", "VN", "C", "NI1", "NI2", "NI3", "NI4", "NI5", "NI6", "NI7", "NI8"
        ]

    def merge_dict(self, splitted_data: list[str]) -> Dict:
        """
        merge_dict Merge data for Dataprocessing.
        Returns:
            Dict: A HwmDict separated by the predefined separator
        """
        data_as_dict = {}
        classify = Classify(splitted_data)
        return data_as_dict | classify.execute(dict_zip_data(self.__keys))


class Hw2NodeDict(__SectionDict):
    """
    Hw2NoedDict A Hw2Node string is converted to a Dict.
    Args:
        HwmDict (Protocol): Basic representation of Hwm rows as Dict.
    Raises:
        KeyError: The String was not passed with the desired key.
    """
    __keys: list[str] = [
        "ID", "RID", "NI1", "NI2", "NI3", "NI4", "MT", "LB", "NI5", "NI6", "NI7", "NI8", "NI9", "NI10", "NI11", "NI12",
        "NI13", "NI14", "NI15", "MP", "PS", "NA"
        ]

    def merge_dict(self, splitted_data: list[str]) -> Dict:
        """
        merge_dict Merge data for Dataprocessing. Includes Ascii encoding.
        Returns:
            Dict: A HwmDict separated by the predefined separator
        """
        data_as_dict = {}
        classify = Classify(splitted_data)
        return data_as_dict | classify.execute(dict_zip_data(self.__keys))
