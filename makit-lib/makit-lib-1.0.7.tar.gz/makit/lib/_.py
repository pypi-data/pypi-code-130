#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author: LiangChao
@email：liang20201101@163.com
@desc: 
"""


class NULL:
    """
    表示空，可用于区分None值
    """

    def __bool__(self):
        return False

    def __or__(self, other):
        return other
