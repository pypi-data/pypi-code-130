#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author: LiangChao
@email：liang20201101@163.com
@desc: 
"""
import re
from typing import Iterable

__all__ = [
    'Dict',
    'List',
    'Str',
    'Input',
    'InputError'
]


class Dict(dict):
    def __getattr__(self, item):
        try:
            return super().__getattribute__(item)
        except AttributeError:
            return self.get(item)

    def __setattr__(self, key, value):
        self[key] = value

    def __getitem__(self, item):
        value = super().__getitem__(item)
        return _wrap(value)

    def get(self, key, default=None):
        value = super().get(key, default)
        return _wrap(value)

    def items(self):
        for k, v in dict.items(self):
            yield k, _wrap(v)


class List(list):
    def __init__(self, sequence):
        super().__init__(sequence)
        self._defaults = sequence

    def reset(self):
        """
        重置，不同的是不会清空所有数据，而会保留构造函数初始传入的数据
        :return:
        """
        self.clear()
        for item in self._defaults:
            self.append(item)

    def is_default_value(self, value):
        return value in self._defaults

    def remove(self, *values, raise_error=True):
        for value in values:
            try:
                super().remove(value)
            except ValueError:
                if raise_error:
                    raise

    def append(self, value, unique=False):
        if unique and value in self:
            return
        super().append(value)

    def insert(self, index, value, unique=False):
        if unique and value in self:
            return self.index(value)
        super().insert(index, value)
        return index

    def index(self, value, start=None, stop=None, raise_error=True) -> int:
        try:
            return super().index(value, start, stop)
        except ValueError:
            if raise_error:
                raise
            return -1

    def extend(self, iterable, unique=False) -> None:
        for item in iterable:
            self.append(item, unique=unique)

    def __iter__(self):
        for item in list.__iter__(self):
            yield _wrap(item)

    def __getitem__(self, item):
        value = list.__getitem__(self, item)
        return _wrap(value)


def _wrap(value):
    if isinstance(value, str):
        return value
    elif isinstance(value, dict):
        return Dict(**value)
    elif isinstance(value, Iterable):
        return List(value)
    else:
        return value


class Str(str):
    def __new__(cls, o, *args, **kwargs):  # 重写 __new__ 否则无法正常重写 __init__
        return super().__new__(cls, o)

    def ints(self):
        """
        获取字符串中所有的整数
        :return:
        """
        _list = re.compile(r'\d+').findall(self)
        return [int(n) for n in _list]

    def floats(self):
        """
        获取字符串中所有的浮点数
        :return:
        """
        _list = re.compile(r'\d+(?:\.\d+)?').findall(self)
        return [float(n) for n in _list]

    def camel(self):
        """
        将下划线字符串转为驼峰风格
        """
        s = ''.join([s.title() if s else '_' for s in self.split('_')])
        return s

    def uncamel(self, sep='_'):
        """
        将驼峰风格字符串转换为下划线风格
        :param sep:
        :return:
        """
        s = re.sub('([a-z]+)(?=[A-Z])', r'\1' + sep, self)
        return s.lower()

    def join(self, *objects, raise_error=False) -> str:
        """
        将多个字符串连接成一个字符串，但会忽略None和空字符串
        Concatenate any number of strings. It will ignore None.
        :param objects:
        :param raise_error:
        :return:
        """

        def iterate():
            for item in objects:
                if item is None or str(item) == '' and not raise_error:
                    continue
                yield item

        return self.join(iterate())

    def split_at(self, sep=None, *positions):
        """
        Split the string at specified positions.
        :param sep: The delimiter according which to split the string.
        :param positions: split positions
        :return:
        """
        parts = self.split(sep)
        result, length = [], len(parts)
        positions = sorted(set([min(length, max(0, i if i >= 0 else length + i)) for i in positions] + [0, length]))
        prev = positions[0]
        for pos in positions:
            if pos <= prev:
                continue
            result.append(sep.join(parts[prev:pos]))
            prev = pos
        return result


class Input:
    @classmethod
    def get(cls, prompt, default=None, ign_case=False):
        """
        获取控制台输入，如果忽略大小写，则返回被转换为小写的输入
        :param prompt: 提示文字
        :param default: 没有输入时的默认值
        :param ign_case: 是否忽略大小写，默认False
        :return:
        """
        v = input(prompt)
        if ign_case:
            v = v.lower()
        return v or default

    @classmethod
    def bool(cls, prompt, default=True, true_options=None, false_options=None):
        """
        将控制台输入转换为布尔值返回
        :param prompt: 提示文字
        :param default: 默认True
        :param true_options: 允许转换为True的输入，默认：true, yes, y, 1
        :param false_options: 允许转换为False的输入，默认：false, no, n, 0
        :return: 如果无法按要求被转换，将返回原输入
        """
        if true_options is None:
            true_options = ['true', '1', 'yes', 'y']
        if false_options is None:
            true_options = ['false', '0', 'no', 'n']
        v = input(prompt).strip().lower()
        if v in true_options:
            return True
        elif v in false_options:
            return False
        else:
            return default

    @classmethod
    def int(cls, prompt, default=0, error=None):
        """
        将控制台输入转换为整型值
        :param prompt: 提示文字
        :param default: 默认为0
        :param error: 输入不是整型数值时的打印消息
        :return:
        """
        v = input(prompt).strip()
        if not v:
            return default
        try:
            return int(v)
        except ValueError:
            if not error:
                error = 'Please input an int value!'
            print(error)
            raise

    @classmethod
    def float(cls, prompt, default=0.0, error=None):
        """
        将控制台输入转换为浮点值
        :param prompt: 提示文字
        :param default: 默认为0
        :param error:
        :return:
        """
        v = input(prompt).strip()
        if not v:
            return default
        try:
            return float(v)
        except ValueError:
            if error:
                print(error)
            else:
                print('Please input a float value!')
            raise


class InputError(Exception):
    """"""
