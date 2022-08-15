import base64
import json
import logging
import struct
import sys

import base58

from nftools.utils import run_command, string_between

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


async def get_mp_metadata(session, token_id, rpc):
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
    async with session.post(rpc, data=json.dumps(post_data)) as resp:
        r = await resp.json()
        data_encoded = r['result']['value']['data'][0]
        data_bytes = base64.b64decode(data_encoded)
        metadata = unpack_mp_metadata(data_bytes)
        return metadata


async def get_account_info(session, token_id, rpc):
    data = {"method": "getAccountInfo", "jsonrpc": "2.0", "params": [token_id, {"encoding": "jsonParsed"}], "id": "1"}
    async with session.post(rpc, data=json.dumps(data)) as resp:
        r = await resp.json()
        return r['result']['value']['data']['parsed']['info']['owner']
