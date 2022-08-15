# -*- coding: utf-8 -*-
import traceback
import time
import os
import urllib.request
from example_demo.request_downloader.downloaders import get_request_content, get_random_ua
import example_demo.commons.common_fun as common
import datetime

import example_demo.setting as setting
from example_demo.utils.redis_client import get_proxy_from_redis
from example_demo.request_downloader.http_downloader import HTTPDownloader
import pandas as pd

class RequestProcess():

    def __init__(self, request_info, debug=False, **kwargs):
        self.request_info = request_info
        self.debug = debug

    def request_get_res(self):
        if setting.REDIS_PROXY_DB and not self.request_info.get("proxies"):
            self.request_info["proxies"] = get_proxy_from_redis()
        if setting.SOURCE_NEED_UA and not common.try_get(self.request_info, ["headers", "User-Agent"]):
            if not self.request_info.get("headers"):
                self.request_info["headers"] = {}
            self.request_info["headers"]["User-Agent"] = get_random_ua()
        self.request_info["debug"] = self.debug
        if self.debug:
            print(self.request_info)
        res = get_request_content(**self.request_info)
        return res


class HTTPBase():
    def __init__(self, request_info: dict, file_download_info: list, **kwargs):
        self.request_info = request_info
        self.file_download_info = file_download_info
        self.option_args = kwargs
        pass

    def get_all_source(self):
        """Returns source for the program."""
        all_source = []
        url = self.request_info.get("url")
        for source in url:
            source_info = {"request_info": self.request_info, "file_download_info": source}
            all_source.append({"info": source_info, "result": True})
        return all_source

    def download_source(self, source):
        """Returns source download result"""

        pass


class HttpDownloadParseBase():
    def __init__(self, source: dict, **kwargs):
        '''
        source need {"info":{},"result":True or False}
        "info" is your prepare source ==> {"request_info":{}, "file_download_info":{}}
        '''
        self.source = source

    def download_parse_source(self):
        """

        parse download result or file or you can customize yourself

        """
        file_download_info = self.source.get("file_download_info")
        file = file_download_info.get("file")
        file_download_path_dir = file_download_info.get("file_download_path_dir")
        if file and file_download_path_dir:
            file_download_path = os.path.join(file_download_path_dir, file)
            return self.request_file_download_process(file_download_path)

        request_info = self.source.get("request_info")
        data_params = request_info.get("url_params")
        page_scan = False
        page_key = ''
        process_res = True
        if data_params:
            for k, param in data_params.items():
                if param == '{page}':
                    page_scan = True
                    page_key = k
        if page_scan:
            self.http_page_process(page_key)
        pass

    def http_page_process(self, page_key):
        # (('size',page_size),('page',page),('start_time','20220719'),('end_rime','20220719'))
        request_url_start_page = self.source.get("request_url_start_page") or 1

        request_url_stop_page = self.source.get("request_url_stop_page")

        data_params = self.source.get("url_params")
        data_params[page_key] = request_url_start_page
        # 未指定截止页数时,可通过自定义,
        # if not request_url_stop_page:
        #     pass
        # else:
        while True:
            download_res, res_content = HTTPDownloader(self.source).downloader()

            need_next = self.parse_customize(res_content, source=self.source, page=data_params.get(page_key))

            if not need_next or (request_url_stop_page and data_params.get(page_key) > request_url_stop_page):
                break
            data_params[page_key] += 1

    def parse_customize(self, res_content, source, **kwargs):
        pass

    def request_file_download_process(self, file_download_path):
        download_res = self.http_get_file(file_download_path)
        if download_res and os.path.exists(file_download_path):
            try:
                data_info = self.parse_downloadfile(file_download_path)
                db_info = self.insert_db_info()
                self.parse_insert_db(db_info, data_info)
            except Exception as e:
                download_res = False
                traceback.print_exc()
        return download_res

    def http_get_file(self, file_download_path):
        request_info = self.source.get("request_info")
        url = request_info.get("url")
        download_res = True
        try:
            urllib.request.urlretrieve(url, file_download_path)
        except Exception as e:
            download_res = False
        return download_res

    def parse_downloadfile(self, file_download_path):
        data = pd.read_csv(file_download_path)
        return data

    def insert_db_info(self):
        '''
        插入数据库信息
        '''
        db_info = {
            "connect_url": '',  # sqlalchemy connect_url if has no need next db host.etc info
            "db_type": '',
            "host": '',
            "port": '',
            "user": '',
            "password": '',
            "table": '',

            # "get_sql": [''],
            # pd.to_sql可选参数
            "to_sql_params": {"if_exists": 'append', "index": False}

        }

        return db_info

    def parse_insert_db(self, db_info, data):
        connect_url = db_info.get("connect_url")
        table = db_info.get("table")
        if connect_url and table and data:
            from onedatautil.request_downloader.sql_downloader import SqlalchemyCon
            client = SqlalchemyCon(connect_url)
            to_sql_params = db_info.get("to_sql_params")
            client.df_to_sql(table, data, **to_sql_params)
