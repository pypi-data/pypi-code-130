#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author: LiangChao
@email：liang20201101@163.com
@desc: 
"""
import asyncio


class Callback:
    def __init__(self, func, count=None):
        self.func = func
        self.count = count

    def __call__(self, *args, **kwargs):
        if self.count is not None:
            self.count -= 1
        if asyncio.iscoroutinefunction(self.func):
            try:
                loop = asyncio.get_running_loop()
            except:
                loop = asyncio.new_event_loop()
            loop.run_until_complete(self.func(*args, **kwargs))
        else:
            return self.func(*args, **kwargs)

    def __repr__(self):
        return f'<Callback {self.func.__name__}>'


class Event:
    """
    事件
    """

    def __init__(self):
        self.owner_class = None
        self._values = {}
        self._callbacks = []

    def clear(self):
        """
        清空所有事件回调
        :return:
        """
        self._callbacks.clear()

    def trigger(self, *args, **kwargs):
        """
        触发事件回调
        :param args:
        :param kwargs:
        :return:
        """
        asyncio.new_event_loop()
        for callback in [*self._callbacks]:
            callback(*args, **kwargs)
            if callback.count == 0:
                self._callbacks.remove(callback)

    def iter_trigger(self, *args, **kwargs):
        """
        迭代方式触发事件回调，允许根据需要中断
        :param args:
        :param kwargs:
        :return:
        """
        for callback in [*self._callbacks]:
            result = callback(*args, **kwargs)
            if callback.count == 0:
                self._callbacks.remove(callback)
            yield result

    def __add__(self, other):
        if isinstance(other, tuple):
            callback, count = other
            assert callable(callback) and (count is None or isinstance(count, int))
            self._callbacks.append(Callback(*other))
        else:
            assert callable(other), f'Event callback must be callable: {other}'
            self._callbacks.append(Callback(other, None))
        return self

    def __call__(self, count=None):
        def deco(func):
            self._callbacks.append(Callback(func, count))
            return func

        return deco
