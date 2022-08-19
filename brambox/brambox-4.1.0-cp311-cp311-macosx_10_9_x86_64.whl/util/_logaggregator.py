#
#   Copyright EAVISE
#   Author: Tanguy Ophoff
#
#   Log aggregator that filters similar error messages and shows them only once
#   This tool is not meant to be used publicly, and is created to reduce the logging clutter when using the EVAL objects.
import logging

__all__ = ['LogAggregator']


class LogAggregator:
    def __init__(self, msg=None):
        self.logger = logging.getLogger('brambox')
        self.msg = msg
        self.set = set()

    def __enter__(self):
        for handler in self.logger.handlers:
            handler.addFilter(self)

    def __exit__(self, type, value, traceback):
        for handler in self.logger.handlers:
            handler.removeFilter(self)

    def filter(self, record):
        info = (record.levelno, record.getMessage())
        if info in self.set:
            return False
        else:
            self.set.add(info)
            if self.msg is not None:
                record.msg = self.msg.format(record.msg)
                return True
