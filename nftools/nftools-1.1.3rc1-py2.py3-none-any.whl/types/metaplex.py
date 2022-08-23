import struct
from dataclasses import dataclass
from typing import List

import base58


@dataclass
class MetaplexMetadataAccountData:
    """Data Class for Metaplex Metadata Account"""

    @dataclass
    class Data:
        name: str
        symbol: str
        uri: str
        seller_fee_basis_points: int
        creators: List[bytes]
        verified: bool
        share: List[int]

    is_mutable: bool
    mint: bytes
    primary_sale_happened: bool
    update_authority: bytes
    data: Data

    @classmethod
    def from_bytes(cls, encoded_data: bytes):
        data = encoded_data
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
        return cls(
            update_authority=source_account.decode("utf-8"),
            mint=mint_account.decode("utf-8"),
            primary_sale_happened=primary_sale_happened,
            is_mutable=is_mutable,
            data=MetaplexMetadataAccountData.Data(
                name=bytes(name).decode("utf-8").strip("\x00"),
                symbol=bytes(symbol).decode("utf-8").strip("\x00"),
                uri=bytes(uri).decode("utf-8").strip("\x00"),
                seller_fee_basis_points=fee,
                creators=[creator.decode("utf-8") for creator in creators],
                share=share,
                verified=verified
            ))


@dataclass
class MetaplexNFT:
    """Dataclass for Metaplex Meta Data SPL Tokens"""
    metadata_pubkey: str
    account_metadata: MetaplexMetadataAccountData
    mint_pubkey: str
    token_account: str = None
    owner: str = None

    @classmethod
    def from_bytes(cls, pubkey, encoded_data: bytes):
        account_metadata = MetaplexMetadataAccountData.from_bytes(encoded_data)
        mint = account_metadata.mint
        return cls(metadata_pubkey=pubkey, account_metadata=account_metadata, mint_pubkey=mint)
