#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author: LiangChao
@email：liang20201101@163.com
@desc: 
"""
import inspect
from types import FunctionType, ModuleType, MethodType

__all__ = [
    'HookCaller',
    'HookError',
    'HookProperty'
]

from makit.lib import fn, py

import inspect


class Interface:
    def __init__(self):
        self.impls = []

    def __add__(self, impl):
        if inspect.isroutine(impl):
            self.impls.append(impl)
        return self

    def __getattribute__(self, item):
        v = object.__getattribute__(item)
        if inspect.isroutine(v):

            def iter_call(*args, **kwargs):
                for impl in self.impls:
                    yield impl(*args, **kwargs)

            return iter_call
        else:
            return v


class Hook:

    def __init__(self, once_run=False, first_result=False):
        self._once_run = once_run
        self._first_result = first_result
        self.callbacks = []
        self._already_run = False

    @property
    def once_run(self):
        return self._once_run

    def __add__(self, other):
        if inspect.isroutine(other):
            self.callbacks.append(other)
        return self

    def __call__(self, *args, **kwargs):
        if self._once_run and self._already_run:
            return
        results = []
        for callback in self.callbacks:
            out = callback(*args, **kwargs)
            if self._first_result:
                return out
            results.append(callback(*args, **kwargs))
        return results


class HookCaller:
    """
    钩子调用器
    """

    def __init__(self):
        self.__hooks = []
        self.__calling_records = {}

    def __getattr__(self, item):
        try:
            v = super().__getattribute__(item)
            return v
        except AttributeError:
            self._method = item
            return self

    def __iter__(self):
        for hook in self.__hooks:
            yield hook

    def __call__(self, *args, first_result=False, once_run=False, **kwargs):
        if once_run and self.__calling_records.get(self._method):
            return
        results = []
        for hook in self.__hooks:
            method = getattr(hook, self._method, None)
            result = fn.run(method, *args, **kwargs)
            if once_run:
                self.__calling_records[self._method] = True
            if first_result:
                return result
            results.append(result)
        return results

    def add(self, obj):
        if isinstance(obj, str):
            obj = py.parse_obj(obj)
        if inspect.ismodule(obj) or inspect.isclass(obj) or inspect.isroutine(obj):
            self.__hooks.append(obj)
        else:
            raise HookError(f'不支持的钩子：{obj}')


class HookProperty:
    def __init__(self):
        self._instance = None
        self.__hooks = []

    def __get__(self, instance, owner):
        self._instance = instance
        return self.__hooks

    def __set__(self, instance, value):
        self._instance = instance
        if isinstance(value, (tuple, list)):
            for hook in value:
                if hook not in self.__hooks:
                    self.__hooks.append(hook)
        elif isinstance(value, (str, FunctionType, ModuleType, type, MethodType)):
            if value not in self.__hooks:
                self.__hooks.append(value)
        else:
            raise HookError(f'不支持的钩子：{value}')


class HookError(Exception):
    """"""
