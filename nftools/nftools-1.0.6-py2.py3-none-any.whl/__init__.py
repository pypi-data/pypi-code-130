"""Top-level package for nftools."""
import logging
import os.path
import sys
from subprocess import run
from nftools.objects import ColorHandler

__author__ = """Jim Eagle"""
__email__ = 'akajimeagle@pm.me'
__version__ = '1.0.6'

logging.basicConfig(level=logging.INFO, handlers=[ColorHandler()])
logger = logging.getLogger(__name__)
OUTPUT_DIR = os.path.join(os.path.expanduser('~'), 'nftools/')


# Check that solana CLI & spl-token-cli are installed
def check_dependencies():
    try:
        r = run('spl-token', capture_output=True)
    except FileNotFoundError:
        msg = 'spl-token CLI not installed. Please visit: https://spl.solana.com/token for details on installation.'
        logger.error(msg)
        sys.exit(0)
    try:
        r = run('solana', capture_output=True)
    except FileNotFoundError:
        msg = 'Solana CLI not installed. Please visit: https://docs.solana.com/cli/install-solana-cli-tools for details' \
              ' on installation.'
        logger.error(msg)
        sys.exit(0)


check_dependencies()

# Create OUTPUT DIR if Missing
if not os.path.exists(OUTPUT_DIR):
    logger.warning(f'{OUTPUT_DIR} does not exist. Creating.')
    os.mkdir(OUTPUT_DIR)
