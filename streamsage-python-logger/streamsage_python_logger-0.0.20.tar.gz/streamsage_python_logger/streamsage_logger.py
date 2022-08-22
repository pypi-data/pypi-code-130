import logging
from streamsage_python_logger.settings.settings import LoggerSettings
logger_settings = LoggerSettings()


def get_logger(context=logger_settings.APP_CONTEXT):
    logger = logging.getLogger(context)
    return logger

