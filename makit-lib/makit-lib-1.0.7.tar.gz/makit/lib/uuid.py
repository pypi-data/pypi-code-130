#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author: LiangChao
@email：liang20201101@163.com
@desc: 
"""
import string
import uuid


def short_id():
    """
    生成短ID
    :return:
    """
    s = str(uuid.uuid4()).replace("-", '')  # 注意这里需要用uuid4
    buffer = []
    chars = string.digits + string.ascii_letters
    for i in range(0, 8):
        start = i * 4
        end = i * 4 + 4
        val = int(s[start:end], 16)
        buffer.append(chars[val % 62])
    return "".join(buffer)
