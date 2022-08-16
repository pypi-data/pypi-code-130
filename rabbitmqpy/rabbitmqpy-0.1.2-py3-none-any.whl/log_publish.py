# coding:utf-8

import os
import json
import socket
import threading
from .publish import Puber
from datetime import datetime


class LogPuber():
    def __init__(self, filepath, *args, backup=7, **kwargs):
        self.puber = Puber(*args, **kwargs)
        self.pid = os.getpid()
        self.hostname = socket.gethostname()
        self.filepath = filepath
        self.backup = backup

    def _log(self, level, *msg):
        now_str = str(datetime.now())
        t = threading.currentThread()
        if msg:
            logs = "%s|%s|host:%s|pid:%s|t:%s|log:%s" % (
                    now_str,
                    level,
                    self.hostname,
                    self.pid,
                    t.ident,
                    msg[0])
            for i in msg[1:]:
                logs = "%s\n%s|%s|pid:%s|t:%s|log:%s" % (
                        logs,
                        now_str,
                        level,
                        self.hostname,
                        self.pid,
                        t.ident,
                        i)
            self.puber.send(json.dumps({
                    "filepath": self.filepath,
                    "backup": self.backup,
                    "logs": logs
                }))

    def info(self, *msgs):
        self._log("INFO", *msgs)

    def error(self, *msgs):
        self._log("ERROR", *msgs)

    def warning(self, *msgs):
        self._log("WARNING", *msgs)

    def warn(self, *msgs):
        self._log("WARN", *msgs)

    def debug(self, *msgs):
        self._log("DEBUG", *msgs)


if __name__ == "__main__":
    amqp_url = 'amqp://10.12.3.162:32037'
    logger = LogPuber(
        "/root/user/logs/mq_test_one.log",
        amqp_url,
        'imlf_mqlog_test',
        'direct',
        routing_key='imlf_mqlog_key_test')
    logger.info("test log")
