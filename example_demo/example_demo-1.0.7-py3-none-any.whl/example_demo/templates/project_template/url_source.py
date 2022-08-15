# -*- coding: utf-8 -*-
import os
from example_demo.commons.common_fun import check_path
import datetime
from example_demo.utils.sqldb_client import SqlDbClient
import example_demo.setting as setting
from example_demo.program_process.process_source_get_cfg import get_source_cfg

'''
数据源信息整理输出

可自定义，可直接加载cfg配置信息
'''


class UrlSourceBase(object):
    def __init__(self, work_path=os.getcwd(), **kwargs):
        self.work_path = work_path
        self.init_work_path()

    def init_work_path(self):
        cwd_path = os.getcwd()
        if cwd_path != self.work_path:
            setting.reload_setting(self.work_path)


# 集群项目
DPOOL_KEY = ''


def get_dpool_init_items():
    pass


class UrlSource(UrlSourceBase):

    def __init__(self, origin_sour=None, **kwargs):
        self.origin_sour = origin_sour
        # self.init_work_path()
        # self.setting_info = kwargs.get("setting_info") or setting.setting_info
        #
        # if kwargs:
        #     self.setting_info.update(kwargs)
        super().__init__(**kwargs)

    def check_outdata(self, url_source):
        # all_has = False

        # vendordb1_connect_url = r'mssql+pymssql://sa:Wind2011@sh-vendordb1\vendordb/SecurityMaster'
        # sql_client = SqlDbClient(vendordb1_connect_url)
        # query_sql = ''
        # df = sql_client.read_sql(query_sql)
        # return all_has ,url_source
        pass

    def load_all_source(self):
        all_source = []
        # if not self.setting_info.get("source_get_customize"):
        if not setting.SOURCE_GET_CUSTOMIZE:

            all_source = get_source_cfg(**self.setting_info)
        else:
            # 自定义数据源信息
            pass
        return all_source

    def load_source_dpool(self, cfg_sour):
        # cfg_sour.update(self.origin_sour)
        # return cfg_sour
        pass
