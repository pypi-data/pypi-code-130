#
# Copyright 2022 aiohomekit team
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from __future__ import annotations

import logging
import random
from typing import Any, Callable, Generator, TypeVar, cast

from bleak import BleakClient
from bleak.backends.characteristic import BleakGATTCharacteristic

from aiohomekit.controller.ble.key import DecryptionKey, EncryptionKey
from aiohomekit.exceptions import EncryptionError
from aiohomekit.model.services import ServicesTypes
from aiohomekit.pdu import (
    OpCode,
    PDUStatus,
    decode_pdu,
    decode_pdu_continuation,
    encode_pdu,
)
from aiohomekit.protocol.tlv import TLV

from .bleak import BLEAK_EXCEPTIONS, AIOHomeKitBleakClient
from .const import AdditionalParameterTypes
from .structs import BleRequest

logger = logging.getLogger(__name__)

WrapFuncType = TypeVar("WrapFuncType", bound=Callable[..., Any])

DEFAULT_ATTEMPTS = 2
MAX_REASSEMBLY = 50
ATT_HEADER_SIZE = 3
KEY_OVERHEAD_SIZE = 16


def retry_bluetooth_connection_error(attempts: int = DEFAULT_ATTEMPTS) -> WrapFuncType:
    """Define a wrapper to retry on bluetooth connection error."""

    def _decorator_retry_bluetooth_connection_error(func: WrapFuncType) -> WrapFuncType:
        """Define a wrapper to retry on bleak error.

        The accessory is allowed to disconnect us any time so
        we need to retry the operation.
        """

        async def _async_wrap(*args: Any, **kwargs: Any) -> Any:
            for attempt in range(attempts):
                try:
                    return await func(*args, **kwargs)
                except BLEAK_EXCEPTIONS:
                    if attempt == attempts - 1:
                        raise
                    logger.debug(
                        "Bleak error calling %s, retrying...", func, exc_info=True
                    )

        return cast(WrapFuncType, _async_wrap)

    return cast(WrapFuncType, _decorator_retry_bluetooth_connection_error)


def _determine_fragment_size(
    client: AIOHomeKitBleakClient,
    encryption_key: EncryptionKey | None,
    handle: BleakGATTCharacteristic,
) -> int:
    """Determine the fragment size for a characteristic based on the MTU."""
    # Newer bleak, not currently released
    if max_write_without_response_size := getattr(
        handle, "max_write_without_response_size", None
    ):
        logger.debug(
            "%s: Bleak max_write_without_response_size: %s, mtu_size-3: %s",
            client.address,
            max_write_without_response_size,
            client.mtu_size - ATT_HEADER_SIZE,
        )
        fragment_size = max(
            max_write_without_response_size, client.mtu_size - ATT_HEADER_SIZE
        )
    # Bleak 0.15.1 and below
    elif (
        (char_obj := getattr(handle, "obj", None))
        and isinstance(char_obj, dict)
        and (char_mtu := char_obj.get("MTU"))
    ):
        logger.debug(
            "%s: Bleak obj MTU: %s, client.mtu_size: %s",
            client.address,
            char_mtu,
            client.mtu_size,
        )
        fragment_size = max(char_mtu, client.mtu_size) - ATT_HEADER_SIZE
    else:
        logger.debug(
            "%s: No bleak obj MTU or max_write_without_response_size, using client.mtu_size-3: %s",
            client.address,
            client.mtu_size - ATT_HEADER_SIZE,
        )
        fragment_size = client.mtu_size - ATT_HEADER_SIZE

    if encryption_key:
        # Secure session means an extra 16 bytes of overhead
        fragment_size -= KEY_OVERHEAD_SIZE

    logger.debug("%s: Using fragment size: %s", client.address, fragment_size)

    return fragment_size


async def ble_request(
    client: AIOHomeKitBleakClient,
    encryption_key: EncryptionKey | None,
    decryption_key: DecryptionKey | None,
    opcode: OpCode,
    handle: BleakGATTCharacteristic,
    iid: int,
    data: bytes | None = None,
) -> tuple[PDUStatus, bytes]:
    """Send a request to the accessory."""
    tid = random.randrange(1, 254)
    await _write_pdu(client, encryption_key, opcode, handle, iid, data, tid)
    return await _read_pdu(client, decryption_key, handle, tid)


async def _write_pdu(
    client: AIOHomeKitBleakClient,
    encryption_key: EncryptionKey,
    opcode: OpCode,
    handle: BleakGATTCharacteristic,
    iid: int,
    data: bytes,
    tid: int,
) -> None:
    """Write a PDU to the accessory."""
    fragment_size = _determine_fragment_size(client, encryption_key, handle)
    # Wrap data in one or more PDU's split at fragment_size
    # And write each one to the target characteristic handle
    writes = []
    for data in encode_pdu(opcode, tid, iid, data, fragment_size):
        logger.debug("Queuing fragment for write: %s", data)
        if encryption_key:
            data = encryption_key.encrypt(data)
        writes.append(data)

    for write in writes:
        await client.write_gatt_char(handle, write, True)


async def _read_pdu(
    client: AIOHomeKitBleakClient,
    decryption_key: DecryptionKey | None,
    handle: BleakGATTCharacteristic,
    tid: int,
) -> tuple[PDUStatus, bytes]:
    """Read a PDU from a characteristic."""
    data = await client.read_gatt_char(handle)
    if decryption_key:
        data = decryption_key.decrypt(data)
        if data is False:
            raise EncryptionError("Decryption failed")

    logger.debug("Read fragment: %s", data)

    # Validate the PDU header
    status, expected_length, data = decode_pdu(tid, data)

    # If packet is too short then there may be 1 or more continuation
    # packets. Keep reading until we have enough data.
    #
    # Even if the status is failure, we must read the whole
    # data set or the encryption will be out of sync.
    #
    while len(data) < expected_length:
        next = await client.read_gatt_char(handle)
        if decryption_key:
            next = decryption_key.decrypt(next)
            if next is False:
                raise EncryptionError("Decryption failed")
        logger.debug("Read fragment: %s", next)

        data += decode_pdu_continuation(tid, next)

    return status, data


def raise_for_pdu_status(client: BleakClient, pdu_status: PDUStatus) -> None:
    """Raise on non-success PDU status."""
    if pdu_status != PDUStatus.SUCCESS:
        raise ValueError(
            f"{client.address}: PDU status was not success: {pdu_status.description} ({pdu_status.value})"
        )


def _decode_pdu_tlv_value(
    client: AIOHomeKitBleakClient, pdu_status: PDUStatus, data: bytes
) -> bytes:
    """Decode the TLV value from the PDU."""
    raise_for_pdu_status(client, pdu_status)
    decoded = dict(TLV.decode_bytes(data))
    return decoded[AdditionalParameterTypes.Value.value]


async def char_write(
    client: BleakClient,
    encryption_key: EncryptionKey | None,
    decryption_key: DecryptionKey | None,
    handle: BleakGATTCharacteristic,
    iid: int,
    body: bytes,
) -> bytes:
    """Execute a CHAR_WRITE request."""
    body = BleRequest(expect_response=1, value=body).encode()
    pdu_status, data = await ble_request(
        client, encryption_key, decryption_key, OpCode.CHAR_WRITE, handle, iid, body
    )
    return _decode_pdu_tlv_value(client, pdu_status, data)


async def _pairing_char_write(
    client: AIOHomeKitBleakClient,
    handle: BleakGATTCharacteristic,
    iid: int,
    request: list[tuple[TLV, bytes]],
) -> dict[int, bytes]:
    """Read or write a characteristic value."""
    buffer = bytearray()
    next_write = TLV.encode_list(request)

    for _ in range(MAX_REASSEMBLY):
        data = await char_write(client, None, None, handle, iid, next_write)
        decoded = dict(TLV.decode_bytearray(data))
        if TLV.kTLVType_FragmentLast in decoded:
            logger.debug("%s: Reassembling final fragment", client.address)
            buffer.extend(decoded[TLV.kTLVType_FragmentLast])
            return dict(TLV.decode_bytes(buffer))
        elif TLV.kTLVType_FragmentData in decoded:
            logger.debug("%s: Reassembling fragment", client.address)
            # There is more data, acknowledge the fragment
            # and keep reading
            buffer.extend(decoded[TLV.kTLVType_FragmentData])
            # Acknowledge the fragment
            # We must construct this manually since TLV.encode_bytes
            # current does not know how to encode a 0 length
            next_write = bytes([TLV.kTLVType_FragmentData, 0])
        else:
            return decoded

    raise ValueError(f"Reassembly failed - too many fragments (max: {MAX_REASSEMBLY})")


async def char_read(
    client: AIOHomeKitBleakClient,
    encryption_key: EncryptionKey | None,
    decryption_key: DecryptionKey | None,
    handle: BleakGATTCharacteristic,
    iid: int,
) -> bytes:
    """Execute a CHAR_READ request."""
    pdu_status, data = await ble_request(
        client, encryption_key, decryption_key, OpCode.CHAR_READ, handle, iid
    )
    return _decode_pdu_tlv_value(client, pdu_status, data)


async def drive_pairing_state_machine(
    client: AIOHomeKitBleakClient,
    characteristic: str,
    state_machine: Generator[tuple[list[tuple[TLV, bytes]], list[TLV]], Any, Any],
) -> Any:
    char = client.get_characteristic(ServicesTypes.PAIRING, characteristic)
    iid = await client.get_characteristic_iid(char)

    request, expected = state_machine.send(None)
    while True:
        try:
            decoded = await _pairing_char_write(client, char, iid, request)
            request, expected = state_machine.send(decoded)
        except StopIteration as result:
            return result.value
