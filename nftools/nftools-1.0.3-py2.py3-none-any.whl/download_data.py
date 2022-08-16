import asyncio
import logging
from typing import List

import aiohttp
from tqdm import tqdm

from nftools.solana import get_mp_metadata, get_account_info, get_rpc, get_metaplex_metadata_accounts, \
    get_nft_token_account
from nftools.utils import shorten_rpc

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def get_collection_info(collection_creator, rpc, *, include_token_acct, include_owner, refresh) -> List:
    mints = []
    logger.info(f'Using RPC: {shorten_rpc(rpc)} to get Candy Machine Data for {collection_creator}.')
    metaplex_token_ids = get_metaplex_metadata_accounts(collection_creator, rpc, refresh=refresh)

    async with aiohttp.ClientSession() as session:
        for idx, mint in enumerate(tqdm(metaplex_token_ids, desc="Loading…", ascii=False, ncols=75)):
            metadata = await get_mp_metadata(session, mint, rpc)
            mint_id = metadata['mint'].decode('utf-8')
            valid = [mint_id]

            if include_owner and include_token_acct:
                token_account = await get_nft_token_account(session, mint_id, rpc)
                owner = await get_account_info(session, token_account, rpc)
                valid.extend([token_account, owner])

            elif include_owner:
                token_account = await get_nft_token_account(session, mint_id, rpc)
                owner = await get_account_info(session, token_account, rpc)
                valid.append(owner)

            elif include_token_acct:
                token_account = await get_nft_token_account(session, mint_id, rpc)
                valid.append(token_account)

            mints.append(valid)

    return mints


async def download_collection_data(collection_creator, rpc, *,
                                   include_token_acct=True, include_owner=True, refresh=False) -> List[List]:
    output_data = await get_collection_info(collection_creator,
                                            rpc,
                                            include_token_acct=include_token_acct,
                                            include_owner=include_owner,
                                            refresh=refresh)
    return output_data


if __name__ == '__main__':
    art_drops = 'JCjVuN7a3YcuyjAtTcVFrTTW4rSuwb8hAM6FJPzPgwoR'
    asyncio.run(
        download_collection_data(art_drops, include_token_acct=False, include_owner=False, load_metadata=True,
                                 rpc=get_rpc()))
