from typing import List
import torch
import os
import logging

def disable_logger(logger_name: List):
    for n in logger_name:
        logger = logging.getLogger(n)
        logger.propagate = False