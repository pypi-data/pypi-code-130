#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author: LiangChao
@email：liang20201101@163.com
@desc: 
"""

from makit.lib.logging.colors import Fore
from makit.lib.logging.core import BaseLogger, NOTSET, Level, DEBUG, ERROR, WARN, FATAL, WARNING, INFO
from makit.lib.logging.handlers import TerminalHandler, FileHandler, COLORED_FORMAT

__all__ = [
    'logger',
    'Logger',
    'Level',
    'INFO', 'DEBUG', 'WARN', 'WARNING', 'ERROR', 'FATAL'
]


class Logger(BaseLogger):
    @property
    def parent(self):
        if not self._parent:
            return logger
        return self._parent

    def write_file(self, filename, level=NOTSET, **kwargs):
        """
        将日志写入文件
        :param filename: 文件名或路径名
        :param level: 日志级别
        :param kwargs: 文件写入参数
        :return:
        """
        handler = FileHandler(filename, level, **kwargs)
        self.add_handler(handler)
        return handler


# 基础日志对象，只在控制台打印输出，所有日志记录器都会将日志传递给它
logger = Logger()
logger.add_handler(TerminalHandler(0, format=COLORED_FORMAT))
