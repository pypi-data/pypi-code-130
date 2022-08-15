#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
  @Author: zhangzongliang
  @Date: 2022-08-31 16:54:08
  @Description: 命名转换
  @Email: noaghzil@gmail.com
  @Last Modified time: 2022-08-31 16:55:24
"""
import re


def to_snake_case(x):
    """转下划线命名"""
    return re.sub('(?<=[a-z])[A-Z]|(?<!^)[A-Z](?=[a-z])', '_\g<0>', x).lower()


def to_camel_case(x):
    """转驼峰法命名"""
    return re.sub('_([a-zA-Z])', lambda m: (m.group(1).upper()), x)


def to_upper_camel_case(x):
    """转大驼峰法命名"""
    s = re.sub('_([a-zA-Z])', lambda m: (m.group(1).upper()), x)
    return s[0].upper() + s[1:]


def to_lower_camel_case(x):
    """转小驼峰法命名"""
    s = re.sub('_([a-zA-Z])', lambda m: (m.group(1).upper()), x)
    return s[0].lower() + s[1:]
