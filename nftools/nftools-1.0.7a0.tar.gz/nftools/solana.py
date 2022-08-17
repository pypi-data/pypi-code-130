import base64
import json
import logging
import os
import struct
import sys
import time
from typing import List

import base58
import pandas as pd
import requests
from aiohttp import ClientSession
from nftools import OUTPUT_DIR

from nftools.utils import run_command, string_between, shorten_rpc

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
        logger.warning('RPC updat failed, exiting.')
        sys.exit(1)

    logger.info(process.stdout)


async def get_mp_metadata(session: ClientSession, token_id, rpc):
    def unpack_mp_metadata(data: bytes) -> dict:
        """Decodes Metaplex metadata from binary(?) string"""
        assert (data[0] == 4)
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
            token_id,
            {
                "encoding": "base64"
            }
        ]
    }
    async with session.post(rpc, data=json.dumps(post_data), headers={'Content-Type': 'application/json'}) as resp:
        r = await resp.json()
        data_encoded = r['result']['value']['data'][0]
        data_bytes = base64.b64decode(data_encoded)
        metadata = unpack_mp_metadata(data_bytes)
        return metadata


async def get_account_info(session: ClientSession, token_id, rpc):
    data = {"method": "getAccountInfo", "jsonrpc": "2.0", "params": [token_id, {"encoding": "jsonParsed"}], "id": "1"}
    # print(data)
    async with session.post(rpc, data=json.dumps(data), headers={'Content-Type': 'application/json'}) as resp:
        content = await resp.content.read()
        r = json.loads(content.decode('utf-8'))
        try:
            return r['result']['value']['data']['parsed']['info']['owner']
        except Exception:
            return await get_account_info(session, token_id, rpc)


async def get_nft_token_account(session: ClientSession, token_id, rpc):
    def get_owner(owners):
        for row in owners:
            if row['amount'] == '1':
                return row['address']

    data = {"method": "getTokenLargestAccounts", "jsonrpc": "2.0", "params": [token_id], "id": "1"}
    async with session.post(rpc, data=json.dumps(data), headers={'Content-Type': 'application/json'}) as resp:

        r = await resp.json()

        holders = r['result']['value']
        if not holders:
            return await get_nft_token_account(session, token_id, rpc)

    return get_owner(holders)


def get_metaplex_metadata_accounts(first_creator: str, rpc: str, *, refresh: bool) -> List[str]:
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
    logger.info('Please be patient. This typically takes 5-10 minutes, depending on collection size.')
    save_dir = os.path.join(OUTPUT_DIR, 'metadata_tokens')
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)

    save_path = os.path.join(save_dir, f'{first_creator}.json')

    if os.path.exists(save_path) and not refresh:
        logger.warning(f'Data already exists in {save_path}.')
        logger.warning(f'Loading data from {save_path}.')
        data = pd.read_json(save_path)

    else:

        if refresh:
            logger.warning('Refresh data set. Getting fresh data for metaplex mint ids.')

        r = requests.post(
            url=rpc,
            data=json.dumps(data),
            headers={'Content-Type': 'application/json'}
        )

        if r.status_code in (403, 410):
            logger.error(r.content.decode('utf-8'))
            logger.error(f'RPC: {shorten_rpc(rpc)} does not allow this function. Please change your rpc and try again.')
            logger.error(f'Try: https://solana-api.projectserum.com')
            sys.exit(0)

        elif r.status_code != 200:
            logger.error(r.content.decode('utf-8'))
            logger.error(f'Unhandled Error!')
            logger.error(f'Try: https://solana-api.projectserum.com')
            sys.exit(0)

        data = r.json()

        logger.info(f'Successfully retrieved metadata token accounts. Saving to \'{save_path}\'.')
        with open(save_path, 'w') as f:
            f.write(json.dumps(data))

    mints = [r['pubkey'] for r in data['result']]
    return mints
