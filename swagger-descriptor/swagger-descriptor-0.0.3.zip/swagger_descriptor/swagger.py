#!/usr/bin/env python
# -*- coding=utf-8 -*-
from typing import Dict, List

from .json_schema import JsonSchema


class Swagger(dict):
    def __init__(self, swagger: Dict):
        super().__init__(swagger)
        self._definitions = swagger.get("definitions", {})
        self._apis: List[APIDescriptor] = []
        for url, url_info in swagger.get("paths", {}).items():
            for method, method_info in url_info.items():
                self._apis.append(self._parse_api(method, url, method_info))

    @property
    def apis(self):
        return self._apis

    @property
    def definitions(self):
        return self._definitions

    def get_definition_by_ref(self, ref):
        map = self._swagger
        for key in ref.split("/")[1:]:
            map = map[key]
        return JsonSchema(map)

    def _parse_api(self, method: str, url: str, descriptor: Dict):
        return APIDescriptor(method, url, descriptor)


class APIDescriptor(object):
    def __init__(self, method, url, descriptor):
        self.__method = method
        self.__url = url
        self.__summary = descriptor.get("summary", "")
        self.__operation_id = descriptor.get("operationId", "")
        self.__tags = descriptor.get("tags", [])
        self.__description = descriptor.get("description", "")
        self.__path_params: List[JsonSchema] = []
        self.__query_params: List[JsonSchema] = []
        self.__header_params: List[JsonSchema] = []
        self.__body_param: JsonSchema = None
        if "requestBody" in descriptor:
            self.__body_param = JsonSchema.parse(descriptor["requestBody"]["content"]["application/json"]["schema"])
        self.__response: Dict = descriptor["responses"]["200"]
        for param in descriptor.get("parameters", []):
            if param["in"] == "path":
                self.__path_params.append(JsonSchema.parse(param))
            elif param["in"] == "query":
                self.query_params.append(JsonSchema.parse(param))
            elif param["in"] == "header":
                self.__header_params.append(JsonSchema.parse(param))
            elif param["in"] == "body":
                self.__body_param = JsonSchema.parse(param["schema"])
            else:
                raise Exception("Unkown param by: {}".format(param))

    @property
    def method(self):
        return self.__method

    @property
    def url(self):
        return self.__url

    @property
    def summary(self):
        return self.__summary

    @property
    def operation_id(self):
        return self.__operation_id

    @property
    def tags(self):
        return self.__tags

    @property
    def description(self):
        return self.__description

    @property
    def path_params(self):
        return self.__path_params

    @property
    def query_params(self):
        return self.__query_params

    @property
    def header_params(self):
        return self.header_params

    @property
    def body_param(self):
        return self.__body_param

    @property
    def response(self):
        return self.__response
