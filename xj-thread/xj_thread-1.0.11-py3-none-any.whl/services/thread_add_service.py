# encoding: utf-8
"""
@project: djangoModel->thread_add
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 信息添加接口服务
@created_time: 2022/8/8 13:36
"""
from django.db import transaction

from xj_thread.models import ThreadExtendData, Thread, ThreadStatistic
from xj_thread.services.thread_extend_service import ThreadExtendInputService


class ThreadAddService:
    @staticmethod
    def add(params):
        # 扩展字段与主表字段拆分
        # 开启事务，防止脏数据
        form_data, extend_form_data = ThreadExtendInputService(params).transform_param()
        save_id = transaction.savepoint()
        try:
            instance = Thread.objects.create(**form_data)
            if extend_form_data:  # 如果传扩展字段插入
                extend_form_data['thread_id_id'] = instance.id
                ThreadExtendData.objects.create(**extend_form_data)
            ThreadStatistic(thread_id=instance.id).save()
            transaction.savepoint_commit(save_id)
        except Exception as e:
            transaction.rollback(save_id)
            return None, "参数错误，请检查配置：" + str(e)
        return {"id": instance.id}, None
