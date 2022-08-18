#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author: LiangChao
@email：liang20201101@163.com
@desc: 
"""


def encode(value, encoding='utf-8', errors='strict'):
    if isinstance(value, bytes):
        return value
    elif isinstance(value, memoryview):
        return bytes(value)
    return str(value).encode(encoding, errors)


def decode(value, encoding='utf-8', errors='strict'):
    if isinstance(value, bytes):
        return value.decode(encoding=encoding, errors=errors)
    elif isinstance(value, str):
        return value
    else:
        return str(value)
