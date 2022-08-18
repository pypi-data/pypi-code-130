#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author: LiangChao
@email：liang20201101@163.com
@desc: 
"""
import re


def dict_to_query_str(d):
    """
    将字典转换为查询字符串
    :return:
    """
    return '&'.join([k + '=' + str(v) for k, v in d.items()])


def query_str_to_dict(query_str):
    """
    从查询字符串转换并更新键值
    :param query_str:
    :return:
    """
    query_str = query_str + '&'
    p = re.compile(r'[^=&]+=[^=]+(?=&)')
    _list = p.findall(query_str)
    d = {}
    for item in _list:
        _arr = item.split('=', maxsplit=1)
        d[_arr[0]] = _arr[1]
    return d
