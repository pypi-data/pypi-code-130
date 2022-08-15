import asyncio
import base64
import json
import logging
import os
import struct
from typing import List

import aiohttp
import base58
import click as click
import pandas as pd
import requests

OUTPUT_DIR = 'output'
RPC_URI = 'https://hardworking-falling-sponge.solana-mainnet.quiknode.pro/1339efb9786cbc7243f1bebdff66135d5208f450/'
logging.basicConfig(level=logging.INFO, filename=f'download_data.log')
logger = logging.getLogger(__name__)


def get_metaplex_metadata_accounts(first_creator: str, name) -> List[str]:
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

    r = requests.post(
        url=RPC_URI,
        data=json.dumps(data),
        headers={'Content-Type': 'application/json'}
    )
    data = r.json()

    mints = [r['pubkey'] for r in data['result']]
    with open(os.path.join(OUTPUT_DIR, f'{name}.json'), 'w') as f:
        f.write(json.dumps({'data': mints}))

    logger.info(f'Retrieved Metadate Mint Accounts for {first_creator}.')

    return mints


async def get_account_info(session, mint):
    data = {"method": "getAccountInfo", "jsonrpc": "2.0", "params": [mint, {"encoding": "jsonParsed"}], "id": "1"}
    async with session.post(RPC_URI, data=json.dumps(data)) as resp:
        r = await resp.json()
        return r['result']['value']['data']['parsed']['info']['owner']


async def get_metadata(session, mint):

    def unpack_metadata_account(data: bytes) -> dict:
        """Decodes Metaplex metadata from binary(?) string"""
        # assert (data[0] == 4)
        i = 1
        source_account = base58.b58encode(bytes(struct.unpack('<' + "B" * 32, data[i:i + 32])))
        i += 32
        mint_account = base58.b58encode(bytes(struct.unpack('<' + "B" * 32, data[i:i + 32])))
        i += 32
        name_len = struct.unpack('<I', data[i:i + 4])[0]
        i += 4
        name = struct.unpack('<' + "B" * name_len, data[i:i + name_len])
        i += name_len
        symbol_len = struct.unpack('<I', data[i:i + 4])[0]
        i += 4
        symbol = struct.unpack('<' + "B" * symbol_len, data[i:i + symbol_len])
        i += symbol_len
        uri_len = struct.unpack('<I', data[i:i + 4])[0]
        i += 4
        uri = struct.unpack('<' + "B" * uri_len, data[i:i + uri_len])
        i += uri_len
        fee = struct.unpack('<h', data[i:i + 2])[0]
        i += 2
        has_creator = data[i]
        i += 1
        creators = []
        verified = []
        share = []
        if has_creator:
            creator_len = struct.unpack('<I', data[i:i + 4])[0]
            i += 4
            for _ in range(creator_len):
                creator = base58.b58encode(bytes(struct.unpack('<' + "B" * 32, data[i:i + 32])))
                creators.append(creator)
                i += 32
                verified.append(data[i])
                i += 1
                share.append(data[i])
                i += 1
        primary_sale_happened = bool(data[i])
        i += 1
        is_mutable = bool(data[i])
        metadata = {
            "update_authority": source_account,
            "mint": mint_account,
            "data": {
                "name": bytes(name).decode("utf-8").strip("\x00"),
                "symbol": bytes(symbol).decode("utf-8").strip("\x00"),
                "uri": bytes(uri).decode("utf-8").strip("\x00"),
                "seller_fee_basis_points": fee,
                "creators": creators,
                "verified": verified,
                "share": share,
            },
            "primary_sale_happened": primary_sale_happened,
            "is_mutable": is_mutable,
        }
        return metadata

    post_data = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getAccountInfo",
        "params": [
            mint,
            {
                "encoding": "base64"
            }
        ]
    }
    async with session.post(RPC_URI, data=json.dumps(post_data)) as resp:
        r = await resp.json()
        data_encoded = r['result']['value']['data'][0]
        data_bytes = base64.b64decode(data_encoded)
        metadata = unpack_metadata_account(data_bytes)
        return metadata


async def get_token_owner(session, mint):

    def get_owner(owners):
        for row in owners:
            if row['amount'] == '1':
                return row['address']

    data = {"method": "getTokenLargestAccounts", "jsonrpc": "2.0", "params": [mint], "id": "1"}
    async with session.post(RPC_URI, data=json.dumps(data)) as resp:
        r = await resp.json()
        holders = r['result']['value']

    return get_owner(holders)


async def get_collection_info(metaplex_mints):
    mints = []
    async with aiohttp.ClientSession() as session:
        for idx, mint in enumerate(metaplex_mints):
            logger.info(f'Getting Info for Mint #{idx}')
            metadata = await get_metadata(session, mint)
            mint_id = metadata['mint'].decode('utf-8')
            token_account = await get_token_owner(session, mint_id)
            owner = await get_account_info(session, token_account)
            mints.append([mint_id, token_account, owner])

    df = pd.DataFrame(mints, columns=['mint_id', 'token_acct', 'owner'])
    df.to_json('airdrop_final.json')
    df.to_json('artdrops.csv')
    return df


async def main_async(airdrop, collection):
    airdrop_mints = get_metaplex_metadata_accounts(airdrop, 'airdrop_metaplex')
    original_mints = get_metaplex_metadata_accounts(collection, 'og_metaplex')
    airdrop_df = await get_collection_info(airdrop_mints)
    original_df = await get_collection_info(original_mints)

    # Save Files as CSV and
    for df in [('og_final', original_df), ('airdrop_final', airdrop_df)]:
        df[1].to_csv(os.path.join(OUTPUT_DIR, f'{df[0]}.csv'), index=False)


@click.command()
@click.option('--airdrop_collection_creator_one',
              prompt='What is the first creator address of the collection you would like to airdrop?', type=str)
@click.option('--original_collection_creator_one',
              prompt='What is the first creator address of the collection you would like to receive the airdrop',
              type=str)
def main(airdrop_collection_creator_one, original_collection_creator_one):
    asyncio.run(main_async(airdrop_collection_creator_one, original_collection_creator_one))


if __name__ == '__main__':
    # artdrops JCjVuN7a3YcuyjAtTcVFrTTW4rSuwb8hAM6FJPzPgwoR
    # visionary 6oNpLuaME2HbAgUK4aPvLoPof5VnUXxJPL1eGa6zAKk8
    main()
