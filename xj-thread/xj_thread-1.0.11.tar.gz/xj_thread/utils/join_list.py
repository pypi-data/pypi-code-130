# encoding: utf-8
"""
@project: djangoModel->custom_merge
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 用户自定义 字典合并
@created_time: 2022/8/16 15:40
"""


class JoinList:
    def __init__(self, l_list, r_list, l_key="id", r_key="id"):
        self.l_key = l_key
        self.r_key = r_key
        self.l_list = l_list
        self.r_list = r_list
        self.l_k_list = [i[l_key] for i in l_list]
        self.r_k_list = [i[r_key] for i in r_list]

    def left_join(self):
        if not len(self.r_k_list) == len(self.r_list):
            raise Exception("r_key 不是唯一字段,无法映射")
        r_map = {item[self.r_key]: item for item in self.r_list}
        for item in self.l_list:
            if item[self.l_key] in r_map.keys():
                item.update(r_map[item[self.l_key]])
        return self.l_list

    def right_join(self):
        if not len(self.l_k_list) == len(self.l_list):
            raise Exception("r_key 不是唯一字段,无法映射")
        l_map = {item[self.l_key]: item for item in self.l_list}
        for item in self.r_list:
            if item[self.r_key] in l_map.keys():
                item.update(l_map[item[self.r_key]])
        return self.r_list
