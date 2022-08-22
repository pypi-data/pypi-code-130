from dataclasses import dataclass
from datetime import datetime
from enum import Enum, IntEnum
from typing import Dict, Iterable, Union


class EnumEncodingSetting(IntEnum):
    VALUE = 0
    NAME = 1


class EncodingSettingException(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class TypeAssignmentException(Exception):
    def __init__(self, *args):
        super().__init__(*args)


@dataclass
class Compysition:
    def __init__(self, **kwargs):
        for arg, arg_val in kwargs.items():
            if arg in self.__annotations__:
                if not isinstance(arg_val, self.__annotations__[arg]):
                    raise TypeAssignmentException(f"Attempted to assign {arg} to {type(arg_val)}, "
                                                  f"while its type should be {self.__annotations__[arg]}")
                self.__setattr__(arg, arg_val)

    def from_dict(self, dct: Dict):
        for k, v in dct.items():
            target_type = self.__annotations__[k]
            if hasattr(target_type, "__origin__"):
                target_subtype = target_type.__origin__
                if issubclass(target_subtype, Iterable):
                    # assuming only one arg for now - this could have many?
                    target_member_type = target_type.__args__[0]
                    vals = v
                    if issubclass(target_member_type, Compysition):
                        vals = [target_member_type().from_dict(val) for val in vals]
                    v = target_subtype(vals)
            elif issubclass(target_type, Compysition):
                v = target_type().from_dict(v)
            elif issubclass(target_type, Enum):
                if self._enum_encoding_setting() == EnumEncodingSetting.VALUE:
                    v = target_type(v)
                elif self._enum_encoding_setting() == EnumEncodingSetting.NAME:
                    v = target_type[v]
                else:
                    raise EncodingSettingException(
                        f"Unexpected enum encoding type: {self._enum_encoding_setting()}"
                    )
            elif issubclass(target_type, datetime):
                v = self._decode_datetime(v)
            setattr(self, k, v)
        return self

    def to_dict(self):
        dct = dict()
        for k, v in self.__dict__.items():
            if isinstance(v, Iterable) and not isinstance(v, str):
                vals = list()
                for val in v:
                    if isinstance(val, Compysition):
                        vals.append(val.to_dict())
                        continue
                    vals.append(val)
                dct[k] = vals
                continue
            elif isinstance(v, Compysition):
                dct[k] = v.to_dict()
                continue
            elif isinstance(v, Enum):
                if self._enum_encoding_setting() == EnumEncodingSetting.VALUE:
                    v = v.value
                elif self._enum_encoding_setting() == EnumEncodingSetting.NAME:
                    v = v.name
                else:
                    raise EncodingSettingException(
                        f"Unexpected enum encoding type: {self._enum_encoding_setting()}"
                    )
            elif isinstance(v, datetime):
                v = self._encode_datetime(v)
            dct[k] = v
        return dct

    @staticmethod
    def _enum_encoding_setting() -> EnumEncodingSetting:
        """
        Override this to return EnumEncodingSetting.NAME if you want enum names instead of values.
        :return: EnumEncodingSetting.
        """
        return EnumEncodingSetting.VALUE

    @staticmethod
    def _encode_datetime(dt: datetime) -> Union[str, int, float]:
        """
        Encodes datetimes to desired data format. Override this to provide your own format.
        The result should be json encodable; typically either a date string or an epoch time in numerical format.
        Default is ISO-8601 standard format.
        :param dt: the datetime object to format.
        :return: formatted data representing the provided datetime object.
        """
        return dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    @staticmethod
    def _decode_datetime(encoded_dt: Union[str, int, float]) -> datetime:
        """
        Decodes datetime from the data format to datetimes for interaction on your class.
        Will likely expect either a date string or an epoch time in numerical format.
        Default setting is to expect ISO-8601 standard format strings.

        Note: typing on this method is designed to allow overrides.
          While numeric timestamps may be decoded properly by this default function, expected usage is ISO-8601.

        :param encoded_dt: the datetime we expect.
        :return: a datetime object representative of the encoded data provided.
        """
        if isinstance(encoded_dt, str):
            return datetime.strptime(encoded_dt, "%Y-%m-%dT%H:%M:%S.%fZ")
        return datetime.utcfromtimestamp(float(encoded_dt))
