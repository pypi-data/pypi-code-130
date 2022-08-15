#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
  @Author: zhangzongliang
  @Date: 2022-08-09 15:07:47
  @Description: 基础工具包
  @Email: noaghzil@gmail.com
  @Last Modified time: 2022-08-15 17:19:38
"""

import json
from datetime import date
from datetime import datetime
from decimal import Decimal


class ObjectEncoder(json.JSONEncoder):
    """
      日期解密工具
    """
    def default(self, obj):
        if isinstance(obj, bytes):
            return obj.decode()
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(obj, date):
            return obj.strftime("%Y-%m-%d")
        if isinstance(obj, Decimal):
            return int(obj)
        return json.JSONEncoder.default(self, obj)


def filter_dict(params, include_keys):
    """
      按keys，过滤字典中的字段
    """
    return isinstance(params, dict) and isinstance(include_keys, list) and dict(
        filter(lambda x: x[0] in include_keys, params.items())) or {}
