import logging
from colorlog import ColoredFormatter


def setup_logger():
    handler = logging.StreamHandler()

    formatter = ColoredFormatter(
        "[%(asctime)s] %(log_color)s%(levelname)s%(reset)s %(message)s"
    )
    handler.setFormatter(formatter)

    logger = logging.getLogger("ploupy")
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
