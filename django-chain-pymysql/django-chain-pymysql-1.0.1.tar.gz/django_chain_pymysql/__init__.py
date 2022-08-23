# django-chain-pymysql: Easy to use mysql in django.

# @depend chain-pymysql
# @link https://github.com/Tiacx/chain-pymysql
# @copyright Copyright (c) 2022 Tiac
# @license MIT
# @author Tiac <1058514799@qq.com>
# @since 1.0

from django.conf import settings
from chain_pymysql import *


class imysql(imysql):

    @classmethod
    def set_default_connection(cls):
        # 设置默认连接
        for name, options in settings.DATABASES.items():
            global_cursor = cls.connect(options, name=name).cursor()
            break

    @classmethod
    def connect(cls, config: dict, name='default'):
        if name in connections:
            return connections.get(name)

        if not config:
            raise exceptions.RuntimeError((400, '【%s】配置不存在' % name))

        return super().connect({
            'host': config.get('HOST'),
            'user': config.get('USER'),
            'password': config.get('PASSWORD'),
            'port': int(config.get('PORT', '3306')),
            'database': config.get('NAME')
        }, name=name)

    @classmethod
    def switch(cls, name: str, db_name=None, inplace=False):
        if name not in connections:
            config = settings.DATABASES.get(name)
            cls.connect(config, name=name)

        return super().switch(name, db_name, inplace)


# 设置默认连接
imysql.set_default_connection()
