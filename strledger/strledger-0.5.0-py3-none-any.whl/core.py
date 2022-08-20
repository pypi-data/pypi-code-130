import binascii
from enum import IntEnum
from typing import Optional, Union

from ledgerwallet.client import LedgerClient
from ledgerwallet.params import Bip32Path
from ledgerwallet.transport import enumerate_devices
from stellar_sdk import (
    Keypair,
    TransactionEnvelope,
    DecoratedSignature,
    FeeBumpTransactionEnvelope,
)

__all__ = [
    "get_default_client",
    "DeviceNotFoundException",
    "DEFAULT_KEYPAIR_INDEX",
    "Ins",
    "P1",
    "P2",
    "SW",
    "AppInfo",
    "StrLedger",
]

DEFAULT_KEYPAIR_INDEX = 0


class Ins(IntEnum):
    GET_PK = 0x02
    SIGN_TX = 0x04
    GET_CONF = 0x06
    SIGN_TX_HASH = 0x08


class P1(IntEnum):
    NONE = 0x00
    FIRST_APDU = 0x00
    MORE_APDU = 0x80


class P2(IntEnum):
    NON_CONFIRM = 0x00
    CONFIRM = 0x01
    LAST_APDU = 0x00
    MORE_APDU = 0x80


class SW(IntEnum):
    # Status word for fail of transaction formatting.
    TX_FORMATTING_FAIL = 0x6125
    # Status word for denied by user.
    DENY = 0x6985
    # Status word for either wrong Lc or minimum APDU lenght is incorrect.
    WRONG_DATA_LENGTH = 0x6A87
    # Status word for incorrect P1 or P2.
    WRONG_P1P2 = 0x6B00
    # Unknown stellar operation
    UNKNOWN_OP = 0x6C24
    # Unknown stellar operation
    UNKNOWN_ENVELOPE_TYPE = 0x6C25
    # Status word for hash signing model not enabled.
    TX_HASH_SIGNING_MODE_NOT_ENABLED = 0x6C66
    # Status word for unknown command with this INS.
    INS_NOT_SUPPORTED = 0x6D00
    # Status word for instruction class is different than CLA.
    CLA_NOT_SUPPORTED = 0x6E00
    # Status word for wrong response length (buffer too small or too big).
    WRONG_RESPONSE_LENGTH = 0xB000
    # Status word for fail to display address.
    DISPLAY_ADDRESS_FAIL = 0xB002
    # Status word for fail to display transaction hash.
    DISPLAY_TRANSACTION_HASH_FAIL = 0xB003
    # Status word for wrong transaction length.
    WRONG_TX_LENGTH = 0xB004
    # Status word for fail of transaction parsing.
    TX_PARSING_FAIL = 0xB005
    # Status word for fail of transaction hash.
    TX_HASH_FAIL = 0xB006
    # Status word for bad state.
    BAD_STATE = 0xB007
    # Status word for signature fail.
    SIGNATURE_FAIL = 0xB008
    # Status word for fail to check swap params
    SWAP_CHECKING_FAIL = 0xB009
    # Status word for success.
    OK = 0x9000


class DeviceNotFoundException(Exception):
    pass


def get_default_client() -> "StrLedger":
    devices = enumerate_devices()
    if len(devices) == 0:
        raise DeviceNotFoundException
    client = LedgerClient(devices[0])
    return StrLedger(client)


class AppInfo:
    def __init__(self, version: str, hash_signing_enabled: bool) -> None:
        self.version = version
        self.hash_signing_enabled = hash_signing_enabled

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return (
            self.version == other.version
            and self.hash_signing_enabled == other.hash_signing_enabled
        )

    def __str__(self) -> str:
        return f"AppConfiguration(version='{self.version}', hash_signing_enabled={self.hash_signing_enabled})"


class StrLedger:
    def __init__(self, client: LedgerClient) -> None:
        self.client = client

    def get_app_info(self) -> AppInfo:
        data = self.client.apdu_exchange(
            ins=Ins.GET_CONF, p1=P1.FIRST_APDU, p2=P2.LAST_APDU
        )
        hash_signing_enabled = bool(data[0])
        version = f"{data[1]}.{data[2]}.{data[3]}"
        return AppInfo(version=version, hash_signing_enabled=hash_signing_enabled)

    def get_keypair(
        self,
        keypair_index: int = DEFAULT_KEYPAIR_INDEX,
        confirm_on_device: bool = False,
    ) -> Keypair:
        path = Bip32Path.build(f"44'/148'/{keypair_index}'")
        data = self.client.apdu_exchange(
            ins=Ins.GET_PK,
            data=path,
            p1=P1.NONE,
            p2=P2.CONFIRM if confirm_on_device else P2.NON_CONFIRM,
        )
        keypair = Keypair.from_raw_ed25519_public_key(data)
        return keypair

    def sign_transaction(
        self,
        transaction_envelope: Union[TransactionEnvelope, FeeBumpTransactionEnvelope],
        keypair_index: int = DEFAULT_KEYPAIR_INDEX,
    ) -> None:
        sign_data = transaction_envelope.signature_base()
        keypair = self.get_keypair(keypair_index=keypair_index)

        path = Bip32Path.build(f"44'/148'/{keypair_index}'")
        payload = path + sign_data
        signature = self._send_payload(payload)
        assert isinstance(signature, bytes)
        decorated_signature = DecoratedSignature(keypair.signature_hint(), signature)
        transaction_envelope.signatures.append(decorated_signature)

    def sign_transaction_hash(
        self,
        transaction_hash: Union[str, bytes],
        keypair_index: int = DEFAULT_KEYPAIR_INDEX,
    ) -> bytes:
        if isinstance(transaction_hash, str):
            transaction_hash = binascii.unhexlify(transaction_hash)
        path = Bip32Path.build(f"44'/148'/{keypair_index}'")
        payload = path + transaction_hash

        data = self.client.apdu_exchange(
            ins=Ins.SIGN_TX_HASH, data=payload, p1=P1.FIRST_APDU, p2=P2.LAST_APDU
        )
        return data

    def _send_payload(self, payload) -> Optional[Union[int, str]]:
        chunk_size = 255
        first = True
        while payload:
            if first:
                p1 = P1.FIRST_APDU
                first = False
            else:
                p1 = P1.MORE_APDU

            size = min(len(payload), chunk_size)
            if size != len(payload):
                p2 = P2.MORE_APDU
            else:
                p2 = P2.LAST_APDU

            resp = self.client.apdu_exchange(Ins.SIGN_TX, payload[:size], p1, p2)
            if resp:
                return resp
            payload = payload[size:]
