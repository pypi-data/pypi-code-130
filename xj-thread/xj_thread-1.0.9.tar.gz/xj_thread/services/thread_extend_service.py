# encoding: utf-8
"""
@project: djangoModel->extend_service
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 扩展服务
@created_time: 2022/7/29 15:14
"""

from ..models import ThreadExtendField, Thread, ThreadExtendData
from ..utils.model_handle import *


class ThreadExtendInputService:
    thread_extend_filed = None

    def __init__(self, form_data, need_all_classify=False):
        """
        :param form_data: 表单
        :param need_all_field: 是否需要全部的扩展字段（查询的时候会用到）
        """
        self.form_data = form_data
        if form_data.get('classify_id', None):
            self.form_data['classify_id_id'] = self.form_data.pop('classify_id')
        if form_data.get('category_id', None):
            self.form_data['category_id_id'] = self.form_data.pop('category_id')

        if need_all_classify:
            self.thread_extend_filed = parse_model(ThreadExtendField.objects.all())
            self.thread_extend_filed = {item["field"]: item["extend_field"] for item in self.thread_extend_filed if self.thread_extend_filed}
        else:
            # 新增或者修改的时候
            if "id" in self.form_data.keys():  # 修改时候：传了id,没有传classify_id
                thread = Thread.objects.filter(id=self.form_data.get('id')).first()
                self.thread_extend_filed = {
                    item["field"]: item["extend_field"]
                    for item in ThreadExtendField.objects.filter(category_id_id=thread.category_id.id).values('field', 'extend_field')
                }
            if self.form_data.get('category_id_id', None):
                self.thread_extend_filed = {
                    item["field"]: item["extend_field"]
                    for item in ThreadExtendField.objects.filter(category_id_id=self.form_data.get('category_id_id')).values('field', 'extend_field')
                }

    # 请求参数转换
    def transform_param(self):
        # 没有定义扩展映射直接返回，不进行扩展操作
        if self.thread_extend_filed is None:
            return self.form_data, None
        extend_data = {self.thread_extend_filed[k]: self.form_data.pop(k) for k, v in self.form_data.copy().items() if k in self.thread_extend_filed.keys()}
        return self.form_data, extend_data


# 所有的输出信息服务都需要有统一的公共方法,
# 暂时定位output
class ThreadExtendOutPutService():
    # extend_field:扩展数据表的字段如field_1,field_2....
    # field:配置的字段映射
    filed_list = None
    extend_field_map = None  # {extend_field:field}
    field_map = None  # {field:extend_field}

    finish_data = None  # 最终完成映射的扩展数据字典

    def __init__(self, category_id_list=None, thread_id_list=None):
        if category_id_list is None:
            raise Exception("id_list 必传")
        if thread_id_list is None:
            raise Exception("id_list 必传")

        self.category_id_list = category_id_list
        self.thread_id_list = thread_id_list

        # 字段映射关系
        self.filed_list = list(ThreadExtendField.objects.filter(category_id__in=self.category_id_list).values("extend_field", "field"))
        self.extend_field_map = {item['extend_field']: item['field'] for item in self.filed_list}
        self.field_map = {item['field']: item['extend_field'] for item in self.filed_list}

    # 获取数据,sql操作
    def get_data(self):
        return list(ThreadExtendData.objects.filter(thread_id__in=self.thread_id_list).values())

    # 同于接口输出
    def out_put(self):
        if self.finish_data is None:
            extend_data = self.get_data()
            finish_data = {}
            for thread_id, v in {item.pop('thread_id_id'): item for item in extend_data}.items():
                temp_dict = {}
                for k, v in v.items():
                    if not v is None and k in self.extend_field_map.keys():
                        temp_dict[self.extend_field_map[k]] = v
                finish_data[thread_id] = temp_dict
            self.finish_data = finish_data
            return finish_data
        return self.finish_data

    def merge(self, merge_set, merge_set_key='id'):
        if self.finish_data is None:
            self.out_put()
        for item in merge_set:
            if item[merge_set_key] in self.finish_data.keys():
                item.update(self.finish_data[item[merge_set_key]])
        return merge_set
