import asyncio
import json
import logging
import os
from typing import List

import aiohttp
import click as click
import pandas as pd
import requests
from tqdm import tqdm

from nftools.solana import get_mp_metadata, get_account_info, get_rpc
from nftools import OUTPUT_DIR
from nftools.utils import shorten_rpc

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_metaplex_metadata_accounts(first_creator: str, load_metadata: bool) -> List[str]:
    """
    Calls getProgramAccounts with Metaplex Metadata Program:
        - Offset 326: [Creater One]
    :param cmid: Candy Machine
    :type cmid:
    :return:
    :rtype:
    """
    data = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getProgramAccounts",
        "params": [
            "metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s",
            {
                "encoding": "base64",
                "filters": [
                    {"memcmp": {"offset": 326, "bytes": f"{first_creator}"}},
                    {"memcmp": {"offset": 358, "bytes": "2"}}
                ]
            }
        ]
    }
    logger.info(f'Getting Metadate Mint Accounts for {first_creator}.')
    debug_path = os.path.join(OUTPUT_DIR, f'{first_creator}.json')

    if not load_metadata:
        r = requests.post(
            url=get_rpc(),
            data=json.dumps(data),
            headers={'Content-Type': 'application/json'}
        )
        data = r.json()

        logger.info(f'Successfully retrieved metadata token accounts. Saving to \'{debug_path}\'.')
        with open(debug_path, 'w') as f:
            f.write(json.dumps(data))

    else:
        logger.warning(f'"Load Metadata" is set. Loading data from {debug_path}.')
        data = pd.read_json(debug_path)

    mints = [r['pubkey'] for r in data['result']]
    return mints


async def get_nft_token_account(session, token_id, rpc):
    def get_owner(owners):
        for row in owners:
            if row['amount'] == '1':
                return row['address']

    data = {"method": "getTokenLargestAccounts", "jsonrpc": "2.0", "params": [token_id], "id": "1"}
    async with session.post(rpc, data=json.dumps(data)) as resp:
        r = await resp.json()
        holders = r['result']['value']

    return get_owner(holders)


async def get_collection_info(collection_creator, rpc, *, include_token_acct, include_owner, load_metadata) -> List:
    mints = []
    rpc = get_rpc()

    logger.info(f'Using RPC: {shorten_rpc(rpc)} to get Candy Machine Data for {collection_creator}.')
    metaplex_token_ids = get_metaplex_metadata_accounts(collection_creator, load_metadata)

    async with aiohttp.ClientSession() as session:
        for idx, mint in enumerate(tqdm(metaplex_token_ids, desc="Loading…", ascii=False, ncols=75)):
            metadata = await get_mp_metadata(session, mint, rpc)
            mint_id = metadata['mint'].decode('utf-8')
            valid = [mint_id]

            if include_owner or include_token_acct:
                token_account = await get_nft_token_account(session, mint_id, rpc)
                valid.append(token_account)

            if include_owner:
                owner = await get_account_info(session, token_account, rpc)
                valid.append(owner)

            mints.append(valid)

    return mints


async def download_collection_data(collection_creator, rpc, *,
                                   include_token_acct=True, include_owner=True, load_metadata=False) -> List[List]:
    output_data = await get_collection_info(collection_creator,
                                            rpc,
                                            include_token_acct=include_token_acct,
                                            include_owner=include_owner,
                                            load_metadata=load_metadata)
    return output_data


if __name__ == '__main__':
    art_drops = 'JCjVuN7a3YcuyjAtTcVFrTTW4rSuwb8hAM6FJPzPgwoR'
    asyncio.run(
        download_collection_data(art_drops, include_token_acct=False, include_owner=False, load_metadata=True, rpc=get_rpc()))
