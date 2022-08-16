#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
  @Author: zhangzongliang
  @Date: 2022-08-09 15:57:50
  @Description:
  @Email: noaghzil@gmail.com
  @Last Modified time: 2022-08-15 17:22:25
"""
from tool_box import filter_dict

def test_filter_dict():
    user_info = {"title": 8, "hospital": "测试医院", "department": "内科", "gender": 1}
    u_format = ["title", "name", "hospital"]
    a = filter_dict(user_info, u_format)
    assert set(a.keys()).difference(u_format) == set()
