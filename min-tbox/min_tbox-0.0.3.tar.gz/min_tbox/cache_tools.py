#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
  @Author: zhangzongliang
  @Date: 2022-08-09 15:03:07
  @Description: 缓存装饰器
  @Email: noaghzil@gmail.com
  @Last Modified time: 2022-08-09 16:01:49
"""
import json
import logging
import inspect
import pickle
import wrapt
from .tools import ObjectEncoder

logger = logging.getLogger(__name__)


class BaseCache(object):
    def __init__(self, cache, delay=60):
        self.cache = cache
        self.delay_s = delay

    def _dumps(self, info):
        if not isinstance(info, str):
            info = json.dumps(info, cls=ObjectEncoder)
        return info

    def _loads(self, info):
        try:
            if isinstance(info, str):
                info = json.loads(info)
        except Exception:
            pass
        return info

    def _one_key(self):
        sig = inspect.signature(self.func).parameters
        f_name = '.'.join([self.func.__module__, self.func.__name__])
        pms_args = zip(list(sig.keys()), self.args)
        pms_d = dict(pms_args)
        pms_d.update(self.kwargs)
        for key in (sig.keys() - pms_d.keys()):
            pms_d[key] = sig[key].default
        no = pickle.dumps((f_name, pms_d))
        logger.info(f"cached|_one_key: {f_name}{pms_d}")
        return no


class ex_cache(BaseCache):
    @wrapt.decorator
    def __call__(self, func, instance, args, kwargs):
        self.func = func
        self.args, self.kwargs = args, kwargs
        res = self._loads(self.cache.get(self._one_key()))
        if not res:
            logger.info("cached: no thing")
            res = self.do_func()
        logger.info("cached: call thing")
        return res

    def do_func(self):
        res = self.func(*self.args, **self.kwargs)
        self.cache.set(self._one_key(), self._dumps(res), ex=self.delay_s)
        return res


class asyc_cache(BaseCache):
    @wrapt.decorator
    async def __call__(self, func, instance, args, kwargs):
        self.func = func
        self.args, self.kwargs = args, kwargs
        res = self._loads(self.cache.get(self._one_key()))
        if not res:
            logger.info("cached: no thing")
            res = await self.do_func()
        logger.info("cached: call thing")
        return res

    async def do_func(self):
        res = await self.func(*self.args, **self.kwargs)
        self.cache.set(self._one_key(), self._dumps(res), ex=self.delay_s)
        return res
