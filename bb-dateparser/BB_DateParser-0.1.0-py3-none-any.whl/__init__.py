__version__ = '0.1.0'

import logging
from .__main__ import DateParser

if logging.getLoggerClass() == logging.Logger:
    from .utils.logger import CustomLogger

    logging.setLoggerClass( CustomLogger )
    log = logging.getLogger("BB-DateParser")
