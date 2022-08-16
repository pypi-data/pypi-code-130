import logging
import logging.config

LOG_CONF = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "default": {
            "format": "%(asctime)s %(levelname)s (pid %(process)d, %(filename)s:%(lineno)s) %(message)s",
            "datefmt": "",
        },
    },
    "handlers": {
        "stdout": {
            "level": "DEBUG",
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "stderr": {
            "level": "ERROR",
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
    },
    "loggers": {
        # module
        "default": {
            "handlers": ["stdout", "stderr"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}


logging.config.dictConfig(LOG_CONF)
logger = logging.getLogger("default")
