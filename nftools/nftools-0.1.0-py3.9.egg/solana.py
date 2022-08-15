import logging
import sys

from .utils import run_command, string_between

logger = logging.getLogger(__name__)


def get_balance(mint):
    msg = run_command(['spl-token', 'accounts', mint]).stdout
    return string_between(msg, '\n-------------\n', '')


def get_rpc():
    command = ['solana', 'config', 'get']
    process = run_command(command).stdout
    rpc = string_between(process, 'RPC URL: ', ' ')
    return rpc


def update_rpc(rpc):
    command = ['solana', 'config', 'set', '-u', rpc]
    process = run_command(command)

    if process.returncode != 0:
        logger.warning('RPC update failed, exiting.')
        sys.exit(1)

    logger.info(process.stdout)
