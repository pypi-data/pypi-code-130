from typing import Callable, Dict, List, Optional, Tuple, Union


## Exceptions
class KeysDoNotMatchLength(Exception):
    """
    KeysDoNotMatch Length of Keys do not match with the dataset

    Args:
        Exception ([type]): Main Class for exceptions
    """

    def __init__(self, values: str, message: str = ""):
        self.values = values
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'Value:{self.values}  -> Msg:{self.message}'


## Classifyer
ClassifyerStrategy = Callable[[Union[list[str], str]], Dict | list]


def list_of_dict(secondary_keys: list[str] = None, range_of_list: int = 5) -> ClassifyerStrategy:
    """
    Args:
        secondary_keys(list[str], optional): a list of keys for the inner dict. normaly the list is empty.
        range_of_list (int, optional): Lists size can be modified like this. Defaults to 5.
    """
    if secondary_keys is None:
        secondary_keys = []

    def splitted_value_as_list(dataset: list[str]) -> list[Dict[str, list]]:
        """
        splitted_value_as_list List is divided into the defined size!

        Args:
            dataset (list[str]): Data set contains all data key and associated data

        Returns:
            Dict[str, list[str]]:  Daten werden in einem dict mit einer liste als value 
        """
        if len(dataset) % range_of_list:
            raise KeysDoNotMatchLength(range_of_list, "The specified length of the list does not match the dataset!")

        return [
            dict(zip(secondary_keys, dataset[count:count + range_of_list]))
            for count, data in enumerate(dataset, start=0) if count % range_of_list == 0
            ]

    return splitted_value_as_list


def dict_zip_data(dict_keys: list[str] = None) -> ClassifyerStrategy:
    """
    Args:
        dict_keys (list[str]): List of key names!
    """

    if dict_keys is None:
        dict_keys = []

    def zip_data_with_keys(dataset: list[str]) -> Dict[str, str]:
        if len(dataset) != len(dict_keys):
            raise KeysDoNotMatchLength(
                ",".join(dict_keys), "The length of the keys does not match the length of the entered data"
                )
        return dict(zip(dict_keys, dataset))

    return zip_data_with_keys


def tuple_of_decode_ascii_code(dict_key: str = "", range_of_data: int = 0) -> ClassifyerStrategy:

    def decode_asccii(dataset: str) -> Dict[str, Tuple[str]]:
        """
        decode_asccii The ascii string is converted to a tuple and returned as a dict. All not needed information will be filtered out. After each Carriage Return (0D) the tuple is terminated.

        Args:
            dataset (str): A pure ascii string should be passed.

        Raises:
            KeysDoNotMatchLength: If the length specified does not match the length of the ascii data.

        Returns:
            Dict[str, Tuple[str]]: A dict with a given key and one or more tuples as value.
        """
        ascii_sentence: Tuple[str] = tuple()
        current_ascii_string = ""
        if len(dataset[::2]) != int(range_of_data):
            raise KeysDoNotMatchLength(
                range_of_data, "The length of the keys does not match the length of the entered data"
                )
        for char_count in range(0, int(range_of_data), 2):
            hex_ascii = dataset[char_count * 2:char_count*2 + 2]
            if hex_ascii == '0D':
                ## 0x0D 	CR:	Carriage Return
                ascii_sentence += (current_ascii_string.strip(), )
                current_ascii_string = ""
                continue
            bytes_object = bytes.fromhex(hex_ascii)
            current_ascii_string += bytes_object.decode("ASCII")
        return {dict_key: ascii_sentence}

    return decode_asccii


class Classify:

    def __init__(self, data: Union[list[str], str]) -> None:
        self.data = data

    def execute(self, used_strategy: ClassifyerStrategy) -> ClassifyerStrategy:
        return used_strategy(self.data)


CreateStringStrategy = Callable[[Union[List[str], Tuple[str]]], Dict]


def create_string_from_dict_with_list_of_dicts(sep: Optional[str] = ";") -> CreateStringStrategy:

    def create_from_dict(dataset: Dict[str, List[str]]) -> str:
        """
        create_string_from_List Create a new string based on the passed data.
        Args:
            dataset (dict[str, List[str]]): a defultdict must be passed otherwise unforeseen errors will occur.
        Returns:
            str: newly created string. Each word is separated with semicolons (csv)
        """
        List_of_elements: List[str] = []
        for elements in dataset:
            for keyword in elements:
                List_of_elements += [str(elements[keyword])]
        return f'{sep}'.join(List_of_elements)

    return create_from_dict


def create_string_from_dict_with_string(sep: Optional[str] = ";") -> CreateStringStrategy:

    def create_from_str(dataset: Dict[str, str]) -> str:
        """
        create_from_str Create a new string based on the passed data.
        Args:
            dataset (dict[str, str]): a defultdict must be passed otherwise unforeseen errors will occur.
        Returns:
            str: newly created string. Each word is separated with semicolons (csv)
        """

        List_of_elements: List[str] = []
        for key in dataset:
            List_of_elements += [str(dataset[key])]
        return f'{sep}'.join(List_of_elements)

    return create_from_str


def create_ascii_hex() -> CreateStringStrategy:

    def ascii_hex_encode(dataset: Tuple[str]) -> str:
        """
        ascii_hex_encode Tuple is formatted back to ascii. After each character comes NULL. After each tuple element comes a return. The string is always ended with double NULL.
        Args:
            dataset (Tuple[str]): Caution the tuple should not be processed!
        Returns:
            str: A finished ascii block.
        """
        if dataset:
            final_row = ""
            for elements in dataset:
                final_row += '00'.join(hex_ascii.encode('utf-8').hex() for hex_ascii in elements)
                final_row += '000D000A00'
            final_row += "0000"
            return final_row.upper()
        return ""

    return ascii_hex_encode


class Create:

    def __init__(self, data: Dict[str, str]) -> None:
        self.data = data

    def execute(self, used_strategy: CreateStringStrategy) -> CreateStringStrategy:
        return used_strategy(self.data)
