import logging
from .step import Step


class Postflight(Step):
    def process(self, data, inputs, utils):
        logger = logging.getLogger()
        logger.info('in Postflight')
        if inputs['clean_up_download']:
            utils.delete_dirs()
