"""Top-level package for nftools."""
import logging
import os.path

__author__ = """Jim Eagle"""
__email__ = 'akajimeagle@pm.me'
__version__ = '0.2.0'

from nftools.objects import ColorHandler

OUTPUT_DIR = os.path.join(os.path.expanduser('~'), 'nftools/')
logging.basicConfig(level=logging.INFO, handlers=[ColorHandler()])
logger = logging.getLogger(__name__)

# Create OUTPUT DIR if Missing
if not os.path.exists(OUTPUT_DIR):
    logger.warning(f'{OUTPUT_DIR} does not exist. Creating.')
    os.mkdir(OUTPUT_DIR)
