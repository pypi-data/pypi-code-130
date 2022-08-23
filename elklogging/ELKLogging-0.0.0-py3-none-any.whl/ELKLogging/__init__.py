import json
import logging
import os
import sys
import time
import traceback
import inspect
import functools
from functools import wraps
from enum import Enum
from ELKLogging.Handler.FileHandler import FileStreamHandler
from ELKLogging.Handler.LogstashHandler import LogstashHandler
from ELKLogging.Handler.StreamHandler import ConsoleStreamHandler
from ELKLogging.Infra.Singletone import Singletone
from ELKLogging.Infra.SystemMetricsCatcher import SystemMetricsCatcher


class HANDLER(Enum):
    LOGSTASH = LogstashHandler
    STREAM = ConsoleStreamHandler
    FILE = FileStreamHandler


class LOG_LEVEL(Enum):
    DEBUG = 'debug'
    INFO = 'info'
    WARNING = 'warning'
    ERROR = 'error'
    CRITICAL = 'critical'


class Logger(metaclass=Singletone):
    def __init__(self, logger_name='ELK_LOGGER', log_level=logging.INFO, config=None):
        self.end_time = dict()
        self.start_time = dict()
        if config:
            with open(config, "r", encoding='utf-8') as file:
                config_data = json.load(file)
                self.initialize_logger(config_data)
        else:
            self.__logger = logging.getLogger(logger_name)
            self.__logger.setLevel(log_level)
            self.__message_data = {}
            self.flush_message_data()

    @classmethod
    def str_to_class(cls, class_name):
        return getattr(sys.modules[__name__], class_name)

    def initialize_logger(self, config_data):
        self.__logger = logging.getLogger(config_data['root']['logger_name'])
        self.__logger.setLevel(config_data['root']['level'])
        handler_list = config_data['root']['handlers']
        for handler in handler_list:
            handler_class = self.str_to_class(config_data['handlers'][handler]['class'])
            log_level = config_data['handlers'][handler].get('level')
            if handler_class == LogstashHandler:
                host = config_data['handlers'][handler].get('ip')
                port = int(config_data['handlers'][handler].get('port'))
                essential_key_list = config_data['handlers'][handler].get('column_list')
                tmp_handler = LogstashHandler(essential_key_list=essential_key_list, host=host, port=port)
            elif handler_class == FileStreamHandler:
                fmt = config_data['handlers'][handler].get('formatter')
                if fmt in config_data['formatters']:
                    fmt = config_data['formatters'][fmt]['format']
                file_path = config_data['handlers'][handler].get('filename')
                tmp_handler = FileStreamHandler(file_path=file_path, fmt=fmt)
            elif handler_class == ConsoleStreamHandler:
                fmt = config_data['handlers'][handler].get('formatter')
                if fmt in config_data['formatters']:
                    fmt = config_data['formatters'][fmt]['format']
                tmp_handler = ConsoleStreamHandler(fmt=fmt)
            else:
                pass
            tmp_handler.setLevel(log_level)
            self.__logger.addHandler(tmp_handler)
        self.__message_data = {}
        self.flush_message_data()

    @property
    def logger(self):
        return self.__logger

    @logger.setter
    def logger(self, logger_name):
        self.__logger = logging.getLogger(logger_name)

    @property
    def message_data(self):
        return self.__message_data

    @message_data.setter
    def message_data(self, message):
        self.__message_data = message

    def set_message_data(self, key, value):
        self.__message_data[key] = value
        return self.__message_data

    def flush_message_data(self, key_list=['line_id', 'process_id', 'metro_ppid', 'detail_message', 'cpu_usage', 'mem_usage', 'running_time']):
        for key in key_list:
            self.set_message_data(key, '0')

    def add_handler(self, handler):
        self.logger.addHandler(handler)

    def remove_handler(self, handler_list):
        tmp_handler = []
        cnt = 0
        for idx in range(len(self.logger.handlers)):
            idx -= cnt
            if type(self.logger.handlers[idx]) not in handler_list:
                tmp_handler.append(self.logger.handlers[idx])
                self.logger.removeHandler(self.logger.handlers[idx])
                cnt += 1
        return tmp_handler

    def restore_handler(self, handler_list):
        for hand in handler_list:
            self.logger.addHandler(hand)

    def findCaller(self):
        f = sys._getframe()
        if f is not None:
            f = f.f_back.f_back
        while hasattr(f, "f_code"):
            co = f.f_code
            if co.co_name == 'wrapper':
                f = f.f_back
                continue
            if co.co_name == 'light':
                funcName = f.f_locals['self'].id
            else:
                funcName = co.co_name
            self.message_data['sys'] = dict()
            frame = f.f_locals
            if funcName in ['get', 'post'] and 'self' in frame and hasattr(frame['self'], 'endpoint'):
                self.message_data['sys']['%(funcName)s'] = frame['self'].endpoint
            elif funcName in ['run'] and 'args' in frame and len(frame['args']) and type(frame['args'][0]) == functools.partial:
                tempFuncName = str(frame['args'][0].func)
                tempFuncName = tempFuncName[tempFuncName.find('<function ') + 10:tempFuncName.find(' at 0x')]
                self.message_data['sys']['%(funcName)s'] = tempFuncName
            else:
                self.message_data['sys']['%(funcName)s'] = funcName
            self.message_data['sys']['%(lineno)d'] = f.f_lineno
            self.message_data['sys']['%(pathname)s'] = co.co_filename
            self.message_data['sys']['%(module)s'] = os.path.splitext(co.co_filename)[0]
            self.message_data['sys']['%(filename)s'] = os.path.basename(co.co_filename)
            break

    def info(self, message=' ', destination=[HANDLER.LOGSTASH, HANDLER.FILE, HANDLER.STREAM]):
        remove_handler = self.remove_handler([n.value for n in destination])
        self.message_data['message'] = message
        self.message_data['detail_message'] = message
        self.findCaller()
        self.logger.info(self.message_data)
        self.restore_handler(remove_handler)

    def error(self, message=' ', destination=[HANDLER.LOGSTASH, HANDLER.FILE, HANDLER.STREAM]):
        remove_handler = self.remove_handler([n.value for n in destination])
        self.message_data['message'] = message
        self.findCaller()
        self.logger.error(self.message_data)
        self.restore_handler(remove_handler)

    def warning(self, message=' ', destination=[HANDLER.LOGSTASH, HANDLER.FILE, HANDLER.STREAM]):
        remove_handler = self.remove_handler([n.value for n in destination])
        self.message_data['message'] = message
        self.message_data['detail_message'] = message
        self.findCaller()
        self.logger.warning(self.message_data)
        self.restore_handler(remove_handler)

    def debug(self, message=' ', destination=[HANDLER.LOGSTASH, HANDLER.FILE, HANDLER.STREAM]):
        remove_handler = self.remove_handler([n.value for n in destination])
        self.message_data['message'] = message
        self.message_data['detail_message'] = message
        self.findCaller()
        self.logger.debug(self.message_data)
        self.restore_handler(remove_handler)

    def critical(self, message=' ', destination=[HANDLER.LOGSTASH, HANDLER.FILE, HANDLER.STREAM]):
        remove_handler = self.remove_handler([n.value for n in destination])
        self.message_data['message'] = message
        self.message_data['detail_message'] = message
        self.findCaller()
        self.logger.critical(self.message_data)
        self.restore_handler(remove_handler)

    def traceback_error(self):
        return traceback.format_exc()

    def systemlog_tracing_start(self):
        func_name = inspect.currentframe().f_back.f_code.co_name
        self.start_time[func_name] = time.time()
        SystemMetricsCatcher.tracing_start()

    def systemlog_tracing_end(self):
        func_name = inspect.currentframe().f_back.f_code.co_name
        self.end_time[func_name] = time.time()
        cpu_usage, mem_usage = SystemMetricsCatcher.cpu_usage_percent(), SystemMetricsCatcher.tracing_mem()
        running_time = self.end_time[func_name] - self.start_time[func_name]
        self.findCaller()
        self.set_message_data(key='method', value=func_name)
        self.set_message_data(key='cpu_usage', value=cpu_usage)
        self.set_message_data(key='mem_usage', value=mem_usage)
        self.set_message_data(key='running_time', value=running_time)

    # decorator
    def wafer_logstash(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                start_time = time.time()
                SystemMetricsCatcher.tracing_start()
                result = func(*args, **kwargs)
                cpu_usage, mem_usage = SystemMetricsCatcher.cpu_usage_percent(), SystemMetricsCatcher.tracing_mem()
                end_time = time.time()
                frame = sys._getframe().f_locals
                if func.__name__ in ['get', 'post'] and 'args' in frame and len(frame['args']) and hasattr(
                        frame['args'][0], 'endpoint'):
                    self.set_message_data(key='method', value=frame['args'][0].endpoint)
                else:
                    self.set_message_data(key='method', value=func.__name__)
                self.set_message_data(key='cpu_usage', value=cpu_usage)
                self.set_message_data(key='mem_usage', value=mem_usage)
                self.set_message_data(key='running_time', value=end_time - start_time)
                if result and type(result) == str and result.startswith("Traceback") or (
                        hasattr(result, 'status_code') and result.status_code != 200):
                    if 'detail_message' not in self.message_data or self.message_data['detail_message'] == '0':
                        self.set_message_data(key='detail_message', value=result)
                    raise
                self.info(destination=[Logger.HANDLER.LOGSTASH])
                return result
            except Exception:
                self.error(destination=[Logger.HANDLER.LOGSTASH])
                return result
        return wrapper