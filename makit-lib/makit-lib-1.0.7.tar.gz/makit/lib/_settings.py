#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author: LiangChao
@email：liang20201101@163.com
@desc: 用于配置管理，支持继承，也可以将不同框架的配置集成在一起使用
"""
import inspect


class _NotExists:
    """"""

    def __bool__(self):
        return False

    def __or__(self, other):
        return other


not_exist = _NotExists()


class Settings:
    """
    配置
    """

    def __init__(self, user_settings=None, defaults=None, bases=None):
        self.bases = bases or []
        self.user_settings = user_settings
        self._defaults = defaults

    def __getattr__(self, item):
        value = not_exist
        if self.user_settings:
            value = self.__get_value(self.user_settings, item)
        if value == not_exist and self._defaults:
            value = self.__get_value(self._defaults, item)
        if value == not_exist and self.bases:
            for base in self.bases:
                value = self.__get_value(base, item)
                if value is not not_exist:
                    break
        return value

    def __get_value(self, obj, name):
        if inspect.ismodule(obj):
            value = getattr(obj, name, not_exist)
        elif isinstance(obj, dict) and name in obj:
            value = obj.get(name, not_exist)
        else:
            value = getattr(obj, name, not_exist)
        return value

    def __call__(self, user_settings=None, defaults=None, bases=None):
        if not bases:
            bases = [self]
        return Settings(user_settings, defaults, bases)


settings = Settings()


class SettingsNotFoundError(Exception):
    """"""
