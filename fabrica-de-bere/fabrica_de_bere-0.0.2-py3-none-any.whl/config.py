import os
from logging.config import dictConfig

PUNK_API_BASE_URL = os.environ.get("PUNK_API_URL")
MAX_BEERS_PER_PAGE = 80

# retry
RETRY_TOTAL = 10
RETRY_BACKOFF = 0.1
RETRY_FORCELIST = [500, 502, 504, 506]

logger_configuration = {
    "version": 1,
    "formatters": {
        "standard": {
            "class": "logging.Formatter",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "console_handler": {
            "class": "logging.StreamHandler",
            "level": "WARNING",
            "formatter": "standard",
            "stream": "ext://sys.stdout",
        },
        "file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "standard",
            "filename": "logs.log",
            "maxBytes": 50000,
            "backupCount": 7,
            "mode": "a,",
        },
    },
    "loggers": {
        "fabrica_de_bere": {
            "handlers": ["console_handler", "file_handler"],
            "level": "INFO",
            "propagate": False,
        }
    },
}

dictConfig(logger_configuration)
