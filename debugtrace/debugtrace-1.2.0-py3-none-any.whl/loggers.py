# loggers.py
# (C) 2020 Masato Kokubo
# since 1.2.0
__author__  = 'Masato Kokubo <masatokokubo@gmail.com>'

from abc import abstractmethod
import datetime
import logging
from logging import config as logging_config
import os
import sys
from debugtrace import config
from debugtrace import _print as pr

class LoggerBase(object):
    """
    Abstract base class for logger classes.
    """
    @abstractmethod
    def print(self, message: str) -> None:
        """
        Outputs the message.

        Args:
            message (str): The message to output
        """
        pass

class Std(LoggerBase):
    """
    Abstract base class for StdOut and StdErr classes.
    """
    def __init__(self, iostream):
        """
        Initializes this object.

        Args:
            iostream: Output destination
        """
        self.iostream = iostream
    
    def print(self, message: str) -> None:
        """
        Outputs the message.

        Args:
            message (str): The message to output
        """
        pr._print(str(datetime.datetime.now()) + ' ' + message, self.iostream)

class StdOut(Std):
    """
    A logger class that outputs to sys.stdout.
    """
    def __init__(self):
        """
        Initializes this object.
        """
        super().__init__(sys.stdout)

    def __str__(self):
        """
        Returns a string representation of this object.

        Returns:
            str: A string representation of this object
        """
        return 'sys.stdout'

class StdErr(Std):
    """
    A logger class that outputs to sys.stderr.
    """
    def __init__(self):
        """
        Initializes this object.
        """
        super().__init__(sys.stderr)

    def __str__(self):
        """
        Returns a string representation of this object.

        Returns:
            str: A string representation of this object
        """
        return 'sys.stderr'

class Logger(LoggerBase):
    """
    A logger class that outputs using the logging package.
    """
    __slots__ = ['_config_file', '_logger', '_logging_logger_name', '_logging_level', '_logging_level_int']

    def __init__(self, config: config.Config):
        self._config_file = config.logging_config_file
        if os.path.exists(config.logging_config_file):
            logging_config.fileConfig(config.logging_config_file)
        else:
            pr._print('debugtrace: (' + config.config_path + ') logging_config_file = ' + config.logging_config_file + \
                ' (Not found)', sys.stderr)

        self._logger = logging.getLogger(config.logging_logger_name)
        self._logging_logger_name = config.logging_logger_name
        self._logging_level = config.logging_level
        self._logging_level_int = \
            logging.CRITICAL if config.logging_level == 'CRITICAL' else \
            logging.ERROR    if config.logging_level == 'ERROR'    else \
            logging.WARNING  if config.logging_level == 'WARNING'  else \
            logging.INFO     if config.logging_level == 'INFO'     else \
            logging.DEBUG    if config.logging_level == 'DEBUG'    else \
            logging.NOTSET   if config.logging_level == 'NOTSET'   else \
            logging.DEBUG

    def print(self, message: str) -> None:
        """
        Outputs the message.

        Args:
            message (str): The message to output
        """
        self._logger.log(self._logging_level_int, message)

    def __str__(self):
        """
        Returns a string representation of this object.

        Returns:
            str: A string representation of this object
        """
        return "logging.Logger: config file: '" + self._config_file +\
        "', logger name: '" + self._logging_logger_name +\
        "', logging level: " + self._logging_level

class File(LoggerBase):
    """
    A logger class that outputs the file.
    """
#   __slots__ = ['_log_path']
    _log_path: str = ''

    def __init__(self, log_path: str):
        dir_path = os.path.dirname(log_path)
        if os.path.exists(dir_path):
            self._log_path = log_path
        else:
            pr._print("debugtrace: The directory '" + dir_path + "' cannot be found.", sys.stderr)
    
    def print(self, message: str) -> None:
        if self._log_path == '': return

        with open(self._log_path, 'a', 1, 'utf-8', 'strict', '\n') as f:
            pr._print(str(datetime.datetime.now()) + ' ' + message, file=f)

    def __str__(self):
        """
        Returns a string representation of this object.

        Returns:
            str: A string representation of this object
        """
        return "File: '" + self._log_path + "'"
