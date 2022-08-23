import asyncio
import logging
import sys

import click

from nftools import __version__
from nftools.create_whitelist_token import create_wl_token
from nftools.download import dl_snapshot, dl_owners, dl_hashlist, dl_metadata
from nftools.solana import get_rpc, update_rpc
from nftools.utils import query_yes_no, shorten_rpc

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def rpc_handler(ctx, param, value):
    if value is not None:
        set_rpc = get_rpc()
        if value != set_rpc:
            query_yes_no(
                question=f'RPC: {shorten_rpc(value)} is different than currently set RPC: {shorten_rpc(set_rpc)}. Are you sure you want to change it?',
                break_message='RPC Update Request Denied.'
            )
            update_rpc(value)
            return value
    else:
        return get_rpc()


@click.group()
@click.version_option(__version__)
def main():
    """Utilitys for Solana NFTs"""
    pass


@main.command()
@click.option('--amount', '-a', prompt='How many white list tokens would you like to mint?', type=int)
@click.option('--rpc', '-r', default=get_rpc(), callback=rpc_handler, prompt='Desired RPC URL', expose_value=True)
def create_whitelist_token(amount, rpc):
    """Mint n amount of whitelist tokens to your wallet. (CMv2)"""
    create_wl_token(amount, rpc)


@main.command()
@click.option('--collection-creator', '-c',
              prompt='First Creator of the CMV2 Collection to Query', type=str,
              help='First Creator of the CMV2 Collection to Query', required=True)
@click.option('--fmt', '-f',
              type=click.Choice(['json', 'csv', 'xlsx'], case_sensitive=False), default='json',
              prompt='Please enter the specified output format.', required=True, help='File type of saved file.')
@click.option('--rpc', default=get_rpc(), callback=rpc_handler, prompt='Desired RPC URL', expose_value=True,
              help='RPC to use during program execution.')
@click.option('--refresh', is_flag=True, help='Refresh metadata accounts (new mints, updated metadata).')
@click.option('--output', '-o', required=False, show_default=False, help="Choose an output path.")
def get_hash_list(collection_creator, fmt, rpc, refresh, output):
    """Retrieves hash list of collection and saves in specified format"""
    asyncio.run(
        dl_hashlist(collection_creator=collection_creator, rpc=get_rpc(), refresh=refresh, fmt=fmt, output=output))


@main.command()
@click.option('--collection-creator', '-c',
              prompt='First Creator of the CMV2 Collection to Query', type=str,
              help='First Creator of the CMV2 Collection to Query', required=True)
@click.option('--fmt', '-f',
              type=click.Choice(['json', 'csv', 'xlsx'], case_sensitive=False), default='csv',
              prompt='Please enter the specified output format.', required=True, help='File type of saved file.')
@click.option('--rpc', default=get_rpc(), callback=rpc_handler, prompt='Desired RPC URL', expose_value=True,
              help='RPC to use during program execution.')
@click.option('--refresh', is_flag=True, help='Refresh metadata accounts (new mints, updated metadata).')
@click.option('--output', '-o', required=False, show_default=False, help="Choose an output path.")
def get_owners(collection_creator, fmt, rpc, refresh, output):
    """Retrieves amount of collection nfts held by owner and saves in specified format"""
    asyncio.run(
        dl_owners(collection_creator=collection_creator, rpc=get_rpc(), refresh=refresh, fmt=fmt, output=output))


@main.command()
@click.option('--collection-creator', '-c',
              prompt='First Creator of the CMV2 Collection to Query', type=str,
              help='First Creator of the CMV2 Collection to Query', required=True)
@click.option('--fmt', '-f',
              type=click.Choice(['json', 'csv', 'xlsx'], case_sensitive=False), default='csv',
              prompt='Please enter the specified output format.', required=True, help='File type of saved file.')
@click.option('--rpc', default=get_rpc(), callback=rpc_handler, prompt='Desired RPC URL', expose_value=True,
              help='RPC to use during program execution.')
@click.option('--refresh', is_flag=True, help='Refresh metadata accounts (new mints, updated metadata).')
@click.option('--output', '-o', required=False, show_default=False, help="Choose an output path.")
def snapshot(collection_creator, fmt, rpc, refresh, output):
    """Takes snapshot of [owner, token_account, mint_id] and saves in the specified format."""
    asyncio.run(
        dl_snapshot(collection_creator=collection_creator, rpc=get_rpc(), refresh=refresh, fmt=fmt, output=output))


@main.command()
@click.option('--collection-creator', '-c',
              prompt='First Creator of the CMV2 Collection to Query', type=str,
              help='First Creator of the CMV2 Collection to Query', required=True)
@click.option('--fmt', '-f',
              type=click.Choice(['json', 'csv', 'xlsx'], case_sensitive=False), default='json',
              prompt='Please enter the specified output format.', required=True, help='File type of saved file.')
@click.option('--rpc', default=get_rpc(), callback=rpc_handler, prompt='Desired RPC URL', expose_value=True,
              help='RPC to use during program execution.')
@click.option('--refresh', is_flag=True, help='Refresh metadata accounts (new mints, updated metadata).')
@click.option('--output', '-o', required=False, show_default=False, help="Choose an output path.")
def get_metadata(collection_creator, fmt, rpc, refresh, output):
    """Takes snapshot of [owner, token_account, mint_id] and saves in the specified format."""
    asyncio.run(
        dl_metadata(collection_creator=collection_creator, rpc=get_rpc(), refresh=refresh, fmt=fmt, output=output))


if __name__ == '__main__':
    args = sys.argv
    print(args)
    if "--help" in args or len(args) == 1:
        print("Please enter a command!")
    main()
