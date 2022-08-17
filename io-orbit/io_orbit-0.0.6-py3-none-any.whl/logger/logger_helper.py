import requests
from io_orbit.logger.laccuna_logging import get_logger

laccuna_logger = get_logger(__name__)


def call(logger, params):
    try:
        requests.post(logger, json=params)
    except requests.exceptions.RequestException as e:
        laccuna_logger.info("Logger service is not available. Exception is: {e}")
