import logging
from .step import Step


class Preflight(Step):
    def process(self, data, inputs, utils):
        logger = logging.getLogger()
        logger.info('in Preflight')
        utils.creat_dirs()
