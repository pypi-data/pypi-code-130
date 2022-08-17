__doc__ = """
https://docs.djangoproject.com/en/4.0/topics/logging/

https://stackoverflow.com/a/33186558

"""
import logging


class UTCFormatter(logging.Formatter):
    # this formatter in the file to mitigate circular import
    converter = logging.time.gmtime


#
# START of LOGGING SETTINGS
#

DEBUG = "DEBUG"
INFO = "INFO"
WARNING = "WARNING"
ERROR = "ERROR"
CRITICAL = "CRITICAL"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "utc": {
            "()": UTCFormatter,
            "format": "[%(asctime)s.%(msecs)03dZ] %(levelname)s : %(name)s : %(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S",
        }
    },
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "utc"}},
    #
    # root is default logger
    "root": {"handlers": ["console"], "level": WARNING},
    #
    "loggers": {
        #
        # Define logger
        #
        # Hide failed azure login
        "azure.identity": {
            "level": CRITICAL,
        },
        # "azure.core": {
        #     "level": CRITICAL,
        # },
        "akvq": {
            "level": INFO,
        },
    },
}
