import logging
from pathlib import Path
from logult.logger import setup_logging


def setup_log(save_dir='./', name_exp='info.log'):
    save_dir = Path(save_dir)
    save_dir.mkdir(parents=True, exist_ok=True)
    setup_logging(save_dir, exp_name=name_exp)
    logger = get_logger()
    return logger


def get_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    return logger
