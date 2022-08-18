#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author: LiangChao
@email：liang20201101@163.com
@desc: 
"""
import atexit
import multiprocessing
import os
import sys
import threading
import traceback
import typing as t
from datetime import datetime

from makit.lib import fn
from makit.lib.fn import CallInfo
from makit.lib.logging.colors import Fore
from makit.lib.logging.handlers import Handler

CRITICAL = 50
FATAL = CRITICAL
ERROR = 40
WARNING = 30
WARN = WARNING
INFO = 20
DEBUG = 10
NOTSET = 0


class Level:
    """
    日志级别
    """

    def __init__(self, name: str, code: int, color=None):
        self.name = name.upper()
        self.code = code
        self.color = color
        self.logger: t.Optional[BaseLogger] = None

    def __set__(self, instance, value):
        raise LoggingError('Can not change level!')

    def __get__(self, instance, owner):
        self.logger = instance
        return self

    def __call__(self, message, *args, **kwargs):
        if self.code <= 0:
            raise LoggingError(f'Level {self.name} is not callable!')  # TODO return?
        self.logger.log(self, message, *args, **kwargs)

    def __repr__(self):
        return f'<LogLevel {self.name} {self.code}>'


class Record:
    def __init__(self, message, level: Level, caller: CallInfo, stack_info=None, *args, **kwargs):
        self.message = str(message)
        self.level_name = level.name
        self.level_code = level.code
        self._caller = caller
        self.func_name = caller.func_name
        self.lineno = caller.lineno
        self.filepath = caller.filename
        self.filename = os.path.basename(caller.filename)
        self.time = datetime.now()
        self.color = level.color
        self.thread = threading.get_ident()
        self.thread_name = threading.current_thread().name
        self.process = os.getpid()
        self.process_name = multiprocessing.current_process().name
        self.stack_info = stack_info
        if args:
            self.message = self.message.format(*args)
        if kwargs:
            self.message = self.message.format(**kwargs)
        for k, v in kwargs.items():
            setattr(self, k, v)


_loggers = []


def _exit():
    for logger in _loggers:
        logger.exit()


atexit.register(_exit)


class BaseLogger:
    """

    """
    debug = Level(name='DEBUG', code=DEBUG, color=Fore.LIGHTCYAN_EX)
    info = Level(name='INFO', code=INFO, color=Fore.LIGHTGREEN_EX)
    warning = Level(name='WARNING', code=WARNING, color=Fore.LIGHTYELLOW_EX)
    warn = warning
    error = Level(name='ERROR', code=ERROR, color=Fore.LIGHTRED_EX)
    critical = Level(name='CRITICAL', code=CRITICAL, color=Fore.RED)
    fatal = critical

    def __init__(self, level=0, propagate=True):
        self.level = level
        self.handlers: t.List[Handler] = []
        self._lock = threading.Lock()
        self._parent = None
        self.propagate = propagate  # 是否向上传递
        self.disabled = False
        _loggers.append(self)
        self._processors = []  # 日志加工器

    @property
    def parent(self):
        return self._parent

    def add_handler(self, handler):
        with self._lock:
            if handler not in self.handlers:
                self.handlers.append(handler)

    def remove_handler(self, handler):
        with self._lock:
            self.handlers.remove(handler)

    def handle(self, record):
        if self.is_enabled_for(record.level_code):
            for handler in self.handlers:
                if record.level_code >= handler.level:
                    handler.handle(record)
        if self.propagate and self.parent != self:  # 避免logger回调自身
            self.parent.handle(record)

    def sub(self, level=NOTSET, propagate=True):
        sub = self.__class__(level, propagate=propagate)
        sub._parent = self
        return sub

    def is_enabled_for(self, level):
        return not self.disabled and self.level <= level

    def exception(self, message, *args, **kwargs):
        self.log(self.error, message, *args, log_stack=True, **kwargs)

    def log(self, level: Level, message, *args, log_stack=False, invoked_file=None, **kwargs):
        if self.disabled:
            return
        c = fn.parse_caller(invoked_file=invoked_file or __file__)
        if log_stack:
            e_type, e, tb = sys.exc_info()
            if e:
                stack_info = traceback.format_tb(tb)
                stack_info.insert(0, 'Traceback (most recent call last):\n')
                stack_info.append(f'{e_type.__name__}: {e}')
            else:
                stack_info = c.get_stack()
        else:
            stack_info = None
        record = Record(message, level, c, stack_info=stack_info, *args, **kwargs)
        self.handle(record)

    def handler(self, level, format):

        def deco(func):
            class DynamicHandler(Handler):
                def emit(self, record):
                    func(record)

            handler = DynamicHandler(level, format=format)
            self.add_handler(handler)

            return func

        return deco

    def exit(self):
        for handler in self.handlers:
            handler.close()


class LoggingError(Exception):
    """"""
