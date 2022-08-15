import logging
import click
import time

from solana import get_rpc, update_rpc
from utils import query_yes_no, run_command, string_between

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CLUSTER = get_rpc()


def confirm_rpc(cluster):
    if cluster != get_rpc():
        query_yes_no(
            f'Cluster {cluster} does not equal default {CLUSTER}. Are you sure you want to update your RPC?',
            break_message='Update request denied.')
        update_rpc(cluster)

    logger.info(f'Using {cluster} as RPC URL.')


def create_token_mint():
    command = ['spl-token', 'create-token', '--decimals', '0']
    process = run_command(command).stdout
    logger.info(process)
    token = string_between(process, 'Creating token ', '')
    return token


def create_token_account(token):
    command = ['spl-token', 'create-account', token]
    process = run_command(command)
    logger.info(process)


def mint_token(token, amount):
    command = ['spl-token', 'mint', token, str(amount)]
    process = run_command(command)
    logger.info(process)


def create_whitelist_token(amount, cluster):
    # Confirm RPC Is Correct
    confirm_rpc(cluster)

    # Create Token and Token Account
    token = create_token_mint()
    create_token_account(token)

    # Wait for Token Account Confirmation
    time.sleep(5)

    mint_token(token.strip(), amount)
    return token


if __name__ == '__main__':
    create_whitelist_token()
