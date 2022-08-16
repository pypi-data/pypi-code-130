#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from pywkdb.utils.db_base import DbBase
from pywkdb.utils.url_parse import UrlParse
logger = logging.getLogger('MySQLDb')


class OracleDb(DbBase):

    def __init__(self, url, with_tran=False):
        """
        构造函数,初始化数据库连接
        :param url: example oracle://user:passwd@127.0.0.1:1521/orcl
        :param with_tran:
        """
        super(OracleDb, self).__init__(url, with_tran)


if __name__ == '__main__':
    pass
