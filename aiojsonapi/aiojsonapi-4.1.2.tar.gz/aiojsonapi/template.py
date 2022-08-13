"""Module with JSON template creation and request data validation."""

import dataclasses
import json
import typing
from functools import wraps

import aiohttp.web
import aiohttp.web_request

from aiojsonapi.dataclass import BaseDataclass
from aiojsonapi.exception import ApiException, DataMissing, UnknownFields
from aiojsonapi.request import Request
from aiojsonapi.response import BadResponse, GoodResponse


class JSONTemplate:
    """Structure based on dataclasses. Converts dict to dataclass."""

    @classmethod
    def _field_converter(cls, fields: dict) -> list:
        result = []
        for key, value in fields.items():
            if isinstance(value, dict):
                field = dataclasses.make_dataclass(key, cls._field_converter(value))
                if value.get("__type__"):
                    wrapper_type = value.pop("__type__")
                    field = wrapper_type[field]
                    result.append((key, field, dataclasses.field(default=None)))
                else:
                    result.append((key, field))
            elif isinstance(value, typing._GenericAlias):  # pylint: disable=protected-access
                if type(None) in typing.get_args(value):
                    result.append((key, value, dataclasses.field(default=None)))
            else:
                result.append((key, value))

        return result

    def __init__(self, template: dict = None, ignore_unknown=True):
        self.template: BaseDataclass = dataclasses.make_dataclass(
            "JSONTemplate",
            self._field_converter(template),
            bases=(BaseDataclass,),
        )
        self.ignore_unknown = ignore_unknown

    def update_forward_refs(self, **localns):
        """Updates references in template."""

        self.template.update_forward_refs(**localns)
        return self

    def __call__(self, func):
        @wraps(func)
        async def wrap(*args, **kwargs):
            try:
                request = None
                for arg in args:
                    if isinstance(arg, aiohttp.web_request.Request):
                        request = arg
                if await request.read():
                    request = Request(await request.json())
                if self.ignore_unknown:
                    request.data = self.template.cut_unknown(request.data)
                try:
                    request.validated_data = self.template(**request.data)
                except TypeError as error:  # kinda hacky :(
                    error = str(error)
                    path = error.split("'")[1]
                    if "missing" in error:
                        raise DataMissing(path) from None
                    raise UnknownFields(path) from None
                result = await func(request, **kwargs)
                if isinstance(result, aiohttp.web.StreamResponse):
                    return result
                return GoodResponse(result)
            except ApiException as error:
                return BadResponse(error.message, status=error.status)
            except json.decoder.JSONDecodeError:
                return BadResponse("Wrong json data format")
            except BaseException as error:
                return BadResponse(repr(error))
        return wrap
