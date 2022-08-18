#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author: LiangChao
@email：liang20201101@163.com
@desc: 
"""
import os
import re
import socket
import sys
import threading
import traceback
from abc import ABC
from datetime import datetime

from makit.lib._serialize import serialize
from makit.lib.const import DEFAULT_TIME_FORMAT
from makit.lib.errors import NotSupportError
from makit.lib.logging.colors import Fore


class Handler:

    def __init__(self, level, format=None, time_fmt=None):
        self.level = level
        self._format = format
        self.time_fmt = time_fmt or DEFAULT_TIME_FORMAT

    def format(self, record):
        if not self._format:
            return record
        if callable(self._format):
            return self._format(record)
        elif isinstance(self._format, str):
            record_dict = dict(record.__dict__)
            record_dict['time'] = record.time.strftime(self.time_fmt)
            return self._format.format(**record_dict)
        else:
            raise NotSupportError(self._format)

    def handle(self, record):
        try:
            lines = [self.format(record) + '\n']
            stack_info = record.stack_info
            if stack_info:
                if isinstance(stack_info, str):
                    stack_info = stack_info.splitlines()
                for line in stack_info:
                    lines.extend('  ' + line)
            self.emit(''.join(lines).strip())
        except Exception:
            sys.stderr.write('--- Logging error ---\n')
            stack_info = traceback.format_exc()
            sys.stderr.write(stack_info)
            self.handle_error(record)

    def emit(self, formatted_record):
        raise NotImplementedError

    def handle_error(self, record):
        pass

    def close(self):
        pass


class LockableHandler(Handler, ABC):
    """"""

    def __init__(self, level, format=None, time_fmt=None):
        super().__init__(level, format=format, time_fmt=time_fmt)
        self._lock = threading.RLock()

    def handle(self, record):
        with self._lock:
            super().handle(record)


# COLORED_FORMAT = '{color}[{level:1.1s} {time} {filename}:{line}]{end_color} {message}'
COLORED_FORMAT = '{color}[{level_name:1.1s} {time} {filename}:{lineno}]{end_color} {message}'


class StreamHandler(LockableHandler):
    """
    A handler class which writes logging records, appropriately formatted,
    to a stream. Note that this class does not close the stream, as
    sys.stdout or sys.stderr may be used.
    """

    terminator = '\n'

    def __init__(self, level, stream=None, format=None, time_fmt=None):
        super().__init__(level, format=format, time_fmt=time_fmt)
        self._stream = stream

    @property
    def stream(self):
        if not self._stream:
            self._stream = self._open_stream()
        return self._stream

    @stream.setter
    def stream(self, stream):
        if stream is not self._stream:
            with self._lock:
                self.flush()
                prev_stream, self._stream = self._stream, stream
                if hasattr(prev_stream, "close"):
                    prev_stream.close()

    def emit(self, formatted_record):
        if not self.stream:
            return
        self.stream.write(formatted_record + self.terminator)
        self.flush()

    def _open_stream(self):
        raise NotImplementedError

    def flush(self):
        """
        Flushes the stream.
        """
        with self._lock:
            if self._stream and hasattr(self._stream, "flush"):
                self._stream.flush()

    def close(self):
        """
        Closes the stream.
        """
        with self._lock:
            if not self.stream:
                return
            try:
                self.flush()
            finally:
                stream = self.stream
                self.stream = None
                if hasattr(stream, "close"):
                    stream.close()

    def __del__(self):
        self.close()


class TerminalHandler(StreamHandler):

    def format(self, record):
        record_dict = serialize(record)
        record_dict['time'] = record.time.strftime(self.time_fmt)
        record_dict['end_color'] = Fore.RESET
        return self._format.format(**record_dict)

    def _open_stream(self):
        return sys.stderr


class FileHandler(StreamHandler):
    FORMAT = '[{level_name:1.1s} {time} {filename}:{lineno}] {message}'

    def __init__(self, filename, level, mode='a', encoding=None, errors=None, format=FORMAT):
        super().__init__(level, format=format)
        filename = os.fspath(filename)
        self.filename = os.path.abspath(filename)
        self.mode = mode
        self.encoding = encoding
        self.errors = errors
        self._last_ctime = None  # 最后一次创建时间
        self._backup_count = 0
        self._should_rotate = None

    def _open_stream(self):
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)
        self._last_ctime = datetime.now()
        return open(self.filename, self.mode, encoding=self.encoding, errors=self.errors)

    def emit(self, record):
        if self._should_rotate and self._should_rotate(record):
            self._rotate()
        super().emit(record)

    def _rotate(self):
        """
        Do a rollover, as described in __init__().
        """
        self.stream = None
        if self._backup_count <= 0:
            return
        for i in range(self._backup_count - 1, 0, -1):
            sfn = "%s.%d" % (self.filename, i)
            dfn = "%s.%d" % (self.filename, i + 1)
            if os.path.exists(sfn):
                if os.path.exists(dfn):
                    os.remove(dfn)
                os.rename(sfn, dfn)
        dfn = self.filename + ".1"
        if os.path.exists(dfn):
            os.remove(dfn)
        os.rename(self.filename, dfn)

    def rotate(self, backup_count=0, max_bytes=0, interval=None, every=None):
        """
        设置日志rotate方式
        :param backup_count: 备份数
        :param max_bytes: 最大存储的字节数
        :param interval: 间隔时间，单位秒
        :param every: 频次，每小时/天/周
        :return:
        """
        self._backup_count = backup_count

        def should_rotate(record):
            need_rotate = False
            if self._last_ctime:
                if interval and interval > 0:
                    need_rotate = need_rotate or (datetime.now() - self._last_ctime).seconds >= interval
                if every:
                    if every == 'day':
                        need_rotate = need_rotate or datetime.now().day > self._last_ctime.day
                    elif every == 'hour':
                        now_hour, last_hour = datetime.now().hour, self._last_ctime.hour
                        need_rotate = need_rotate or (last_hour == 23 and now_hour == 0) or now_hour > last_hour
                    elif every == 'week':
                        now_wd, last_wd = datetime.now().weekday() + 1, self._last_ctime.weekday() + 1
                        need_rotate = need_rotate or (last_wd == 7 and now_wd == 1) or now_wd > last_wd
                    elif re.match(r'^w\d$', every):  # 每周几
                        need_rotate = need_rotate or 'w' + str(datetime.now().weekday() + 1) == every
            if max_bytes > 0 and need_rotate is False:
                msg = "%s\n" % self.format(record)
                self.stream.seek(0, 2)  # due to non-posix-compliant Windows feature
                need_rotate = self.stream.tell() + len(msg) >= max_bytes
            return need_rotate

        self._should_rotate = should_rotate
        return self

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

    def __hash__(self):
        return hash(self.filename)


class SocketHandler(LockableHandler):
    def __init__(self, level, host, port):
        super().__init__(level)
        self.host = host
        self.port = port
        if port is None:
            self.address = host
        else:
            self.address = (host, port)
        self.sock = None

    def make_socket(self, timeout=1):
        """
        A factory method which allows subclasses to define the precise
        type of socket they want.
        """
        if self.port is not None:
            s = socket.create_connection(self.address, timeout=timeout)
        else:
            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            s.settimeout(timeout)
            try:
                s.connect(self.address)
            except OSError:
                s.close()
                raise
        return s

    def send(self, s):
        if self.sock is None:
            self.make_socket()
        if self.sock:
            try:
                self.sock.sendall(s)
            except OSError:
                self.sock.close()
                self.sock = None

    def handle_error(self, record):
        if self.sock:
            self.sock.close()
            self.sock = None  # try to reconnect next time
        else:
            super().handle_error(record)

    def format(self, record):  # TODO
        pass

    def emit(self, formatted_record):
        self.send(formatted_record)

    def close(self):
        with self._lock:
            sock = self.sock
            if sock:
                self.sock = None
                sock.close()
            super().close()


class QueueHandler(Handler):
    def __init__(self, level, queue, format=None):
        super().__init__(level, format=format)
        self.queue = queue

    def enqueue(self, record):
        self.queue.put_nowait(record)

    def emit(self, record):
        self.enqueue(self.format(record))
