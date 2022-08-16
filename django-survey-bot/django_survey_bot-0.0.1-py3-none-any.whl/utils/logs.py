"""
Import syntax:
from plaintiffhq.core.utils.logs import Logs
"""

class Logs:

    def __log_handler(self, message, log_type):
        pass

    def debug(self, message):
        return self.__log_handler(message, 'Debug')

    def info(self, message):
        return self.__log_handler(message, 'Info')

    def warning(self, message):
        return self.__log_handler(message, 'Warning')

    def error(self, message):
        return self.__log_handler(message, 'Error')

    def celery_error(self, message):
        return self.__log_handler(message, 'CeleryError')



