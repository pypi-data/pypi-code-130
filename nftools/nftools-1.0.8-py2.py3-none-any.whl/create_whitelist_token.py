import logging
import sys
import time

from nftools.solana import get_rpc, update_rpc
from nftools.utils import query_yes_no, run_command, string_between

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
    logger.info(f'Creating white list token.')
    process = run_command(command)
    print(process)
    token = string_between(process.stdout, 'Creating token ', '')

    if token is None:
        raise ValueError(f'Failed to create token: {process.stderr}')

    return token


def create_token_account(token):
    command = ['spl-token', 'create-account', token]
    logger.info(f"Creating token account for {token}.")
    process = run_command(command)
    if process.returncode != 0:
        raise RuntimeError(f'Failed to create token account for {token}.')

    logger.info(f'Successfully created token account for {token}.')


def mint_token(token, amount):
    command = ['spl-token', 'mint', token, str(amount)]
    logger.info(f'Minting {amount} of token {token}.')
    process = run_command(command)
    if process.returncode != 0:
        logger.warning(f'Minting {amount} of {token} failed! {process.stderr}')
        sys.exit(0)
    logger.info(f'Successfully minted {amount} of {token}.')


def create_wl_token(amount, cluster):
    # Confirm RPC Is Correct
    confirm_rpc(cluster)

    # Create Token and Token Account
    token = create_token_mint()
    create_token_account(token)

    # Wait for Token Account Confirmation
    time.sleep(5)

    mint_token(token.strip(), amount)
    return token
