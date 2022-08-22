"""
Base classes with custom attributes for updating, serializing and deserializing data classes and enums.
"""
import json
from abc import ABC
from datetime import date, datetime, tzinfo
from enum import Enum

from pydantic import BaseModel, create_model

from algora.common.function import date_to_timestamp, datetime_to_timestamp


class BaseEnum(str, Enum):
    """
    Base enum class used by all enum classes.

    Note: Inheriting from str is necessary to correctly serialize output of enum
    """
    pass


class Base(ABC, BaseModel):
    """
    Base class used for all data classes.
    """

    class Config:
        # use enum values when using .dict() on object
        use_enum_values = True

        json_encoders = {
            date: date_to_timestamp,
            datetime: datetime_to_timestamp,
            tzinfo: str
        }

    @classmethod
    def cls_name(cls) -> str:
        """
        Get class name.

        Returns:
            str: Class name
        """
        return cls.__name__

    @classmethod
    def new_fields(cls, *args, **kwargs):
        """
        TODO DOCUMENT @will

        Args:
            *args:
            **kwargs:

        Returns:

        """
        return {}

    @classmethod
    def update(cls, *args, **kwargs):
        """
        TODO DOCUMENT @will

        Args:
            *args:
            **kwargs:

        Returns:

        """
        new_fields = cls.new_fields(*args, **kwargs)
        return create_model(cls.__name__, __base__=cls, **new_fields)

    def request_dict(self) -> dict:
        """
        Convert data class to dict. Used instead of `.dict()` to serialize dates as timestamps.

        Returns:
            dict: Serialized data class as dict
        """
        return json.loads(self.json())
