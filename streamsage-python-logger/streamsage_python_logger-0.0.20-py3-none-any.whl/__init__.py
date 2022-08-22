import logging
from logging.config import dictConfig
from pydantic import BaseSettings, validator

from streamsage_python_logger.settings.settings import LoggerSettings
from streamsage_python_logger.logger_configuration.formatters import formatters
from streamsage_python_logger.logger_configuration.handlers import handlers

logger_settings = LoggerSettings()
logging.Logger.level = 1


def trace(self, msg, *args, **kwargs):
    if self.isEnabledFor(1):
        self._log(1, msg, args, **kwargs)


logging.addLevelName(1, 'TRACE')
logging.trace = trace
logging.Logger.trace = trace


class LoggerConfig(BaseSettings):
    context: str = ""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    logger_settings = logger_settings
    LOG_LEVEL: str = logger_settings.LOG_SDK_TRANSPORT_FLUENT_LEVEL
    version = 1
    disable_existing_loggers = False

    formatters = formatters
    handlers = handlers
    loggers = {
        context: {"handlers": logger_settings.LOG_SDK_TRANSPORTS.split(","), "level": LOG_LEVEL},
    }

    class Config:
        validate_assignment = True

    @validator('context')
    def set_name(cls, context):
        return context


dictConfig(LoggerConfig(context=logger_settings.APP_CONTEXT).dict())
