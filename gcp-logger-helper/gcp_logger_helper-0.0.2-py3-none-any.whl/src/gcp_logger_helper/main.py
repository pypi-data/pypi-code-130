import logging
import os
import google.cloud.logging
from dotenv import load_dotenv
from google.cloud.logging.handlers import CloudLoggingHandler


def is_cloud_logging_enabled():
    return os.getenv('ENABLE_CLOUD_LOGGING').__eq__('TRUE')


def is_console_logging_enabled():
    return os.getenv('ENABLE_CONSOLE').__eq__('TRUE')


class Logger(logging.Logger):
    # Define Google Cloud logging levels
    DEFAULT = 0
    DEBUG = 100
    INFO = 200
    NOTICE = 300
    WARNING = 400
    ERROR = 500
    CRITICAL = 600
    ALERT = 700
    EMERGENCY = 800

    # "Register" new logging level
    logging.addLevelName(DEFAULT, 'DEFAULT')
    logging.addLevelName(DEBUG, 'DEBUG')
    logging.addLevelName(INFO, 'INFO')
    logging.addLevelName(NOTICE, 'NOTICE')
    logging.addLevelName(WARNING, 'WARNING')
    logging.addLevelName(ERROR, 'ERROR')
    logging.addLevelName(CRITICAL, 'CRITICAL')
    logging.addLevelName(ALERT, 'ALERT')
    logging.addLevelName(EMERGENCY, 'EMERGENCY')

    def __init__(self, name: str):
        super().__init__(name)
        load_dotenv()
        if is_cloud_logging_enabled():
            client = google.cloud.logging.Client()
            gcl_handler = CloudLoggingHandler(client)
            gcl_handler.setFormatter(logging.Formatter(os.getenv('LOGGER_FORMAT')))
            gcl_handler.setLevel(os.getenv('DEFAULT_LOGGER_LEVEL'))
            self.addHandler(gcl_handler)

        if is_console_logging_enabled():
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter(os.getenv('LOGGER_FORMAT')))
            console_handler.setLevel(os.getenv('DEFAULT_LOGGER_LEVEL'))
            self.addHandler(console_handler)

    def default(self, msg, *args, **kwargs):
        if self.isEnabledFor(self.DEFAULT):
            self._log(self.DEFAULT, msg, args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        if self.isEnabledFor(self.DEBUG):
            self._log(self.DEBUG, msg, args, **kwargs)

    def info(self, msg, *args, **kwargs):
        if self.isEnabledFor(self.INFO):
            self._log(self.INFO, msg, args, **kwargs)

    def notice(self, msg, *args, **kwargs):
        if self.isEnabledFor(self.NOTICE):
            self._log(self.NOTICE, msg, args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        if self.isEnabledFor(self.WARNING):
            self._log(self.WARNING, msg, args, **kwargs)

    def error(self, msg, *args, **kwargs):
        if self.isEnabledFor(self.ERROR):
            self._log(self.ERROR, msg, args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        if self.isEnabledFor(self.CRITICAL):
            self._log(self.CRITICAL, msg, args, **kwargs)

    def alert(self, msg, *args, **kwargs):
        if self.isEnabledFor(self.ALERT):
            self._log(self.ALERT, msg, args, **kwargs)

    def emergency(self, msg, *args, **kwargs):
        if self.isEnabledFor(self.EMERGENCY):
            self._log(self.EMERGENCY, msg, args, **kwargs)
