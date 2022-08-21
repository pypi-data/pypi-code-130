import json
import copy
import pprint
import pathlib

__all__ = ["JsonGeneralizer", "get_json_structure"]


class JsonGeneralizer:
    """
    This class can transform any JSON structure to a general form which doesn't have any
    specific values (string, int, lists etc.) but only indicates on what type of value it is.
    Only the original keys are left unchanged.
    """

    def __init__(self, json_object):
        self.json_object = json_object
        self.generalized_json = None

    def generalize(self):
        """
        This method parses the original JSON object and creates a generalized form of it.

        Example:
            >>> dict_ = {"a": "hello world", "b": {"c": "3"}}
            >>> jg = JsonGeneralizer(dict_)
            >>> jg.generalize()
            {"a": "<str>", "b": {"c": "<int>"}}
        """
        self.generalized_json = self.recurrent_parser(copy.deepcopy(self.json_object))
        self.generalized_json = self.postprocess_generalized_json(self.generalized_json)

    def beautify_json(self, which):
        """
        This method returns the JSON transformed to a beautified string form. It contains
        a parameter which determines which JSON is to be beautified - original or generalized one.

        Args:
        which (str): "original" or "generalized", depending on which JSON is to be beautifed

        Returns:
            (str) beautified version of a JSON

        Example:
            >>> jg = JsonGeneralizer({...})
            >>> print(jg.beautify_json('generalized'))
            {   'document': {'original': '<str>'},
                'reference': {   'negative': {'original': '<str>'},
                                 'positive': {'original': '<str>'}}}
        """

        if which == "original":
            return pprint.pformat(self.json_object, indent=4)
        elif which == "generalized":
            return pprint.pformat(self.generalized_json, indent=4)
        else:
            raise Exception(
                "'which' argument must be equal to 'original' or 'generalized'")

    @staticmethod
    def recurrent_parser(struct):
        """
        This static method takes a JSON structure and recurrently calls itself to generalize all
        nested elements of the JSON.

        Args:
            struct (Union[List, Dict]): any JSON structure (a dict or a list)

        Returns:
            (Union[List, Dict]): the structure with one more level generalized

        Example:
            >>> {"a": "hello world", "b": {"c": "3"}}
            {"a": "<str>", "b": {"c": "<int>"}}
        """

        # simple types
        if type(struct) == int:
            return "<int>"

        if type(struct) == float:
            return "<float>"

        if type(struct) == str:
            return "<str>"

        # dictionary
        if type(struct) == dict:
            for i in struct:
                struct[i] = JsonGeneralizer.recurrent_parser(struct[i])

            return struct

        # list
        if type(struct) == list:
            if all([type(i) == str for i in struct]):
                return "<str_list>"
            if all([type(i) == int for i in struct]):
                return "<int_list>"
            if all([type(i) == float for i in struct]):
                return "<float_list>"
            if all([type(i) != dict and type(i) != list for i in struct]):
                return "<multitype_list>"

            struct_copy = struct.copy()
            for counter, elem in enumerate(struct):
                struct_copy[counter] = JsonGeneralizer.recurrent_parser(elem)
            return struct_copy

    @staticmethod
    def postprocess_generalized_json(struct):
        """
        This static method performs postprocessing on generalized form of the input JSON such as:
        - removing duplicating multiple items (only two left to indicate multiplicity)
        - ...

        Args:
            struct (Union[List, Dict]): generalized JSON

        Returns:
            (Union[List, Dict]): postprocessed generalized JSON

        Example:
            >>> [{"a": "<str>", "b": "<str>"}, {"a": "<str>", "b": "<str>"},
                 {"a": "<str>", "b": "<str>"}, {"a": "<str>", "b": "<str>"}]
            [{"a": "<str>", "b": "<str>"}, {"a": "<str>", "b": "<str>"}]
        """

        if type(struct) == list and len(struct) > 2:
            if struct.count(struct[0]) == len(struct):
                struct = struct[:2]

        return struct


def get_json_structure(json_or_path):
    """
    This function generates structure of a JSON directly, without creating any class instances.

    Args:
        json_or_path (Union[List, Dict, str, pathlib.Path]):
            If the input parameter is interpreted as a path, then JSON file loaded from this path
            is considered. Otherwise, input of this function is treated as a JSON object directly

    Returns:
        (Union[List, Dict]): Structure of the input JSON

    Examples:
        >>> get_json_structure({"a": [1, 2, 3], "b": "hello"})
        {"a": "<int_list>", "b": "<str>"}
        >>> get_json_structure('path/to/file.json')
        {"a": "<int>", "b": {"c": "<float_list>"}}
    """

    if isinstance(json_or_path, str) and ".json" in json_or_path:
        with open(json_or_path, "r") as f:
            input_ = json.load(f)
    elif isinstance(json_or_path, pathlib.Path):
        with open(str(json_or_path), "r") as f:
            input_ = json.load(f)
    elif isinstance(json_or_path, (list, dict)):
        input_ = json_or_path
    else:
        raise TypeError("Input parameter must be a path to .json file or a JSON object")

    generalizer = JsonGeneralizer(input_)
    generalizer.generalize()
    return generalizer.generalized_json
