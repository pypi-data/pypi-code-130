
# Imports the Google Cloud client library
from google.cloud import logging

import structlog
structlog.configure(processors=[structlog.processors.JSONRenderer()])

class DOLogger():
    ENV = 'local'
    NAME = ''
    logger = None
    logging_client = None
    log = None
    live = 'live'

    def __init__(self):
        # Instantiates a client
        self.logging_client = logging.Client()
        self.log = structlog.get_logger()

    def setLogName(self, log_name):
        self.logger = self.logging_client.logger(log_name)
        self.NAME = log_name
    
    def setEnv(self,env):
        self.ENV = env

    def info(self, msg):
        if self.ENV == self.live:
            if self.NAME == '':
                raise Exception('Log name empty. please set log name.')

            self.logger.log_text( msg, severity="INFO")
        else:
            self.log.msg(msg)
    
    def debug(self, msg):
        if self.ENV == self.live:
            if self.NAME == '':
                raise Exception('Log name empty. please set log name.')
            self.logger.log_text( msg, severity="DEBUG")
        else:
            self.log.msg(msg)
    
    def error(self, msg):
        if self.ENV == self.live:
            if self.NAME == '':
                raise Exception('Log name empty. please set log name.')

            self.logger.log_text( msg, severity="ERROR")
        else:
            self.log.msg(msg)
    
    def warning(self, msg):
        if self.ENV == self.live:
            if self.NAME == '':
                raise Exception('Log name empty. please set log name.')

            self.logger.log_text( msg, severity="WARNING")
        else:
            self.log.warning(msg)

    def critical(self, msg):
        if self.ENV == self.live:
            if self.NAME == '':
                raise Exception('Log name empty. please set log name.')

            self.logger.log_text( msg, severity="CRITICAL")
        else:
            self.log.critical(msg)

    def alert(self, msg):
        if self.ENV == self.live:
            if self.NAME == '':
                raise Exception('Log name empty. please set log name.')

            self.logger.log_text( msg, severity="ALERT")
        else:
            self.log.alert(msg)