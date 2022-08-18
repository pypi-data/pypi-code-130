from marshmallow import fields
import typing
from .utils import convert_timestamp_to_date_utc


__all__ = [
    "NestedValueField",
    "DatetimeFromTimeStamp"
]


class NestedValueField(fields.Field):
    """Field that help to get value from nested field when deserializer
    :param nested_key: show where to get value in nested field"""

    def __init__(self, *args, **kwargs):
        if 'data_key' in kwargs and 'nested_key' in kwargs:
            raise Exception('You must define just one of data_key or nested_key.')
        super(NestedValueField, self).__init__(*args, **kwargs)
        self.type_class = kwargs.get('type_class', None)
        self.nested_key = kwargs.get('nested_key', None)


class DatetimeFromTimeStamp(fields.Field):
    """Field that deserializer from timestamp like: 1660622040.0 to datetime object"""

    def _deserialize(
            self,
            value: typing.Any,
            attr: str or None,
            data: typing.Mapping[str, typing.Any] or None,
            **kwargs,
    ):
        if value is None:
            return None
        return convert_timestamp_to_date_utc(value)
