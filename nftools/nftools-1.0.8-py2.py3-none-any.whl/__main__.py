import asyncio
import json
import logging
import os
import pathlib
import sys
from typing import List

import click
from pandas import DataFrame

from nftools import OUTPUT_DIR, __version__
from nftools.create_whitelist_token import create_wl_token
from nftools.download_data import download_collection_data
from nftools.solana import get_rpc, update_rpc
from nftools.utils import query_yes_no, shorten_rpc

logger = logging.getLogger(__name__)


def handle_save(data: DataFrame, name, directory, *, fmt='json', orient='list', output=None):
    if output is None:
        save_dir = os.path.join(OUTPUT_DIR, directory)
        if not os.path.exists(save_dir):
            os.mkdir(save_dir)

        save_path = os.path.join(save_dir, f'{name}.{fmt}')

    else:
        save_path = pathlib.Path(output)
        save_dir = save_path.parent.as_posix()
        if not os.path.exists(save_dir):
            raise NotADirectoryError(f'Output: {output} is not a directory.')

    def save_json():
        d = data.to_dict(orient=orient)
        with open(save_path, 'w') as f:
            f.write(json.dumps(d))

    def save_csv():
        data.to_csv(save_path, index=False)

    def save_xlsx():
        data.to_excel(save_path, index=False)

    formats = {'json': save_json, 'csv': save_csv, 'xlsx': save_xlsx}
    func = formats[fmt]
    func()
    logger.info(f'Successfully saved data to {save_path}.')


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
    mint_ids: List[List[str]] = asyncio.run(download_collection_data(collection_creator=collection_creator,
                                                                     rpc=get_rpc(),
                                                                     include_owner=False,
                                                                     include_token_acct=False,
                                                                     refresh=refresh))

    df = DataFrame(mint_ids, columns=['mint_id'])
    handle_save(data=df, name=f'hash-list_{collection_creator}', directory='hash_lists', fmt=fmt, output=output)


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
    mint_ids: List[List[str]] = asyncio.run(download_collection_data(collection_creator=collection_creator,
                                                                     rpc=get_rpc(),
                                                                     include_owner=True,
                                                                     include_token_acct=False,
                                                                     refresh=refresh))
    df = DataFrame(mint_ids, columns=['mint_id', 'owner'])
    df.to_json(os.path.join(OUTPUT_DIR, f'owners_{collection_creator}.json'))

    grouped = df.groupby(['owner']).size().to_frame(name='nfts').reset_index()
    handle_save(data=grouped, name=f'owners_{collection_creator}', directory='owners', fmt=fmt, orient='records',
                output=output)


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
    mint_ids: List[List[str]] = asyncio.run(download_collection_data(collection_creator=collection_creator,
                                                                     rpc=get_rpc(),
                                                                     include_owner=True,
                                                                     include_token_acct=True,
                                                                     refresh=refresh))
    df = DataFrame(mint_ids, columns=['mint_id', 'token_account', 'owner'])
    handle_save(data=df, name=f'snapshot_{collection_creator}', directory='snapshots', fmt=fmt, orient='records',
                output=output)

    if __name__ == '__main__':
        args = sys.argv
        print(args)
        if "--help" in args or len(args) == 1:
            print("Please enter a command!")
        main()
