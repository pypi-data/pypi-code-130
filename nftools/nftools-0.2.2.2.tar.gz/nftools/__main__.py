import asyncio
import json
import logging
import os
import sys
from functools import partial
from typing import List

import click
from pandas import DataFrame

from nftools.utils import query_yes_no, shorten_rpc

from nftools.download_data import download_collection_data

from nftools.create_whitelist_token import create_wl_token
from nftools.solana import get_rpc, update_rpc
from nftools import OUTPUT_DIR

logger = logging.getLogger(__name__)


def handle_save(data: DataFrame, name, fmt='json'):
    save_path = os.path.join(OUTPUT_DIR, f'{name}.{fmt}')

    def save_json():
        d = data.to_dict(orient='list')
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
    if value is None:
        return

    set_rpc = get_rpc()
    if value != set_rpc:
        query_yes_no(
            question=f'RPC: {shorten_rpc(value)} is different than currently set RPC: {shorten_rpc(set_rpc)}. Are you sure you want to change it?',
            break_message='RPC Update Request Denied.'
        )
        update_rpc(value)


@click.group()
@click.version_option("1.0.0")
def main():
    """Utilitys for Solana NFTs"""
    pass


@main.command()
@click.option('--amount', '-a', prompt='How many white list tokens would you like to mint?', type=int)
@click.option('--rpc', '-r', default=get_rpc(), callback=rpc_handler, prompt='Desired RPC URL', expose_value=True)
def create_whitelist_token(amount, rpc):
    """Search through CVE Database for vulnerabilities"""
    create_wl_token(amount, rpc)


@main.command()
@click.option('--collection-creator', '-c',
              prompt='First Creator of the CMV2 Collection to Query', type=str)
@click.option('--fmt', '-f',
              type=click.Choice(['json', 'csv', 'xlsx'], case_sensitive=False), default='json',
              prompt='Please enter the specified output format.', required=True)
@click.option('--rpc', '-r', default=get_rpc(), callback=rpc_handler, prompt='Desired RPC URL', expose_value=True)
@click.option('--use-downloaded', '-dl', is_flag=True)
def get_hash_list(collection_creator, fmt, rpc, use_downloaded):
    """Retrieves hash list of collection and saves in specified format"""
    mint_ids: List[List[str]] = asyncio.run(download_collection_data(collection_creator=collection_creator,
                                                                     rpc=rpc,
                                                                     include_owner=False,
                                                                     include_token_acct=False,
                                                                     load_metadata=use_downloaded))

    df = DataFrame(mint_ids, columns=['mint_id'])
    handle_save(data=df, name=f'hash-list_{collection_creator}', fmt=fmt)


if __name__ == '__main__':
    args = sys.argv
    print(args)
    if "--help" in args or len(args) == 1:
        print("Please enter a command!")
    main()
