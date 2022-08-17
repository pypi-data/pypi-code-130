import abc
from typing import Union, List, Tuple, Dict, Any

__all__ = [
    "JSONSerializable", "JSONNull", "JSONString", "JSONNumber", "JSONBoolean", "JSONArray", "JSONObject", "JSONType"
]


class JSONSerializable(abc.ABC):
    @abc.abstractmethod
    def __json__(self, context: Dict[str, Any]) -> "JSONType": ...

    @classmethod
    def __subclasshook__(cls, subclass) -> bool:
        return hasattr(subclass, "__json__")


JSONNull = None
JSONString = str
JSONNumber = Union[int, float]
JSONBoolean = bool
JSONArray = Union[List["JSONType"], Tuple["JSONType", ...]]
JSONObject = Dict[str, "JSONType"]
JSONType = Union[JSONNull, JSONString, JSONNumber, JSONBoolean, JSONArray, JSONObject, JSONSerializable]
