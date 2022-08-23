import asyncio
import json
import logging
import os
import pathlib
import time
from dataclasses import asdict
from typing import List

import aiohttp
from aiolimiter import AsyncLimiter
from pandas import DataFrame
from tqdm import tqdm

from nftools import OUTPUT_DIR
from nftools.solana import get_metaplex_metadata_accounts, \
    get_token_account, get_token_owner
from nftools.types.metaplex import MetaplexNFT

logging.basicConfig(level=logging.INFO)
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


async def get_owners(session, nft, rpc, *, limiter, pbar):
    async with limiter:
        nft.token_account = await get_token_account(session, nft, rpc)
    async with limiter:
        nft.owner = await get_token_owner(session, nft, rpc)

    pbar.update(1)
    return nft


async def get_nfts(collection_creator, rpc, *, refresh) -> List[MetaplexNFT]:
    start_time = time.process_time()
    limiter = AsyncLimiter(100, 1)
    nfts: List[MetaplexNFT] = get_metaplex_metadata_accounts(
        collection_creator=collection_creator,
        rpc=rpc,
        refresh=refresh)
    with tqdm(total=len(nfts)) as pbar:
        async with aiohttp.ClientSession() as session:
            tasks = []
            for nft in nfts:
                tasks.append(get_owners(session, nft, rpc, limiter=limiter, pbar=pbar))

            output = await asyncio.gather(*tasks)

    pbar.close()
    logger.info(f'Fetching NFT data took: {start_time * -1 + time.process_time()} seconds')
    return output


async def dl_snapshot(*, collection_creator, rpc, refresh, fmt, output):
    nfts = await get_nfts(collection_creator, rpc, refresh=refresh)
    df = DataFrame([[nft.mint_pubkey, nft.token_account, nft.owner] for nft in nfts],
                   columns=['mint', 'token_account', 'owner'])
    handle_save(data=df, name=f'snapshot_{collection_creator}', directory='snapshots', fmt=fmt, orient='records',
                output=output)


async def dl_owners(*, collection_creator, rpc, refresh, fmt, output):
    nfts = await get_nfts(collection_creator, rpc, refresh=refresh)
    df = DataFrame([[nft.owner, nft.mint_pubkey] for nft in nfts],
                   columns=['owner', 'mint'])
    grouped = df.groupby(['owner']).size().to_frame(name='nfts').reset_index()
    handle_save(data=grouped, name=f'owners_{collection_creator}', directory='owners', fmt=fmt, orient='records',
                output=output)


async def dl_hashlist(*, collection_creator, rpc, refresh, fmt, output):
    nfts: List[MetaplexNFT] = get_metaplex_metadata_accounts(
        collection_creator=collection_creator,
        rpc=rpc,
        refresh=refresh)
    df = DataFrame([nft.mint_pubkey for nft in nfts], columns=['mint_id'])
    handle_save(data=df, name=f'hash-list_{collection_creator}', directory='hash_lists', fmt=fmt, output=output)


async def dl_metadata(*, collection_creator, rpc, refresh, output):
    nfts: List[MetaplexNFT] = get_metaplex_metadata_accounts(
        collection_creator=collection_creator,
        rpc=rpc,
        refresh=refresh)
    rows = [asdict(nft.account_metadata) for nft in nfts]
    data = {'metadata': rows}

    if output is None:
        save_dir = os.path.join(OUTPUT_DIR, 'metadata')
        if not os.path.exists(save_dir):
            os.mkdir(save_dir)

        save_path = os.path.join(save_dir, f'metadata_{collection_creator}.json')
    else:
        save_path = output

    with open(save_path, 'w') as f:
        f.write(json.dumps(data))
