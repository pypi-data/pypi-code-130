import copy

from marshmallow import Schema, pre_load
from .transform_fields import NestedValueField
from .utils import get_value_from_field, remove_none_field
import typing


class BaseSchemaTransform(Schema):
    def _get_value_for_nested_value_field(self, data):
        for attr_name, field_obj in self.load_fields.items():
            if isinstance(field_obj, NestedValueField):
                field_name = (
                    field_obj.nested_key if field_obj.nested_key is not None else attr_name
                )
                data[attr_name] = get_value_from_field(data, field_name, None)

    def _return_type_class_for_nested_field(self):
        load_fields_copy = copy.deepcopy(self.load_fields)
        for attr_name, field_obj in self.load_fields.items():
            if isinstance(field_obj, NestedValueField) and field_obj.type_class is not None:
                attrs_of_field_obj = copy.deepcopy(field_obj.__dict__)
                load_fields_copy[attr_name] = field_obj.type_class(**attrs_of_field_obj)
        self.load_fields = load_fields_copy

    def pre_load_action(self, data, many, **kwargs):
        return data

    @pre_load(pass_many=True)
    def load_nested_field(self, data: dict, many, **kwargs):
        data = self.pre_load_action(data, many, **kwargs)
        data_list = data
        if not many:
            data_list = [data]

        data_list_copy = []
        for data_item in data_list:

            self._get_value_for_nested_value_field(data_item)
            data_item = remove_none_field(data_item)
            data_list_copy.append(data_item)
        self._return_type_class_for_nested_field()

        if not many:
            return data_list_copy[0]
        return data_list_copy

    @classmethod
    def transform(
        cls,
        data: (
            typing.Mapping[str, typing.Any]
            or typing.Iterable[typing.Mapping[str, typing.Any]]
        ),
        *,
        many: bool or None = False,
        partial: bool or None = False,
        unknown: str or None = None,
    ):
        instance = cls(many=many, partial=partial, unknown=unknown)
        return instance.load(data)

    def dump(self, obj: typing.Any, *, many: bool or None = None):
        raise Exception('Method not use.')

    def dumps(self, obj: typing.Any, *args, many: bool or None = None, **kwargs):
        raise Exception('Method not use')
