import grpc
from bluerpc_service.rpc import (
    ble_pb2,
    ble_pb2_grpc,
    common_pb2,
)
import asyncio
from bleak import BleakScanner, BleakClient
import time
import re
from enum import Enum
from functools import partial
from typing import List

def validateMAC(addr: str):
    return bool(
        re.match("^([0-9a-fA-F][0-9a-fA-F]:){5}([0-9a-fA-F][0-9a-fA-F])$", addr)
    )


def validateUUID(u: str):
    return bool(
        re.match(
            "[0-9a-f]{8}-[0-9a-f]{4}-[0-5][0-9a-f]{3}-[089ab][0-9a-f]{3}-[0-9a-f]{12}",
            u,
        )
    )


class VFlags(Enum):
    MAC = 1
    CONN = 2
    SERVICE = 3
    CHARACTERISTIC = 4
    DESCRIPTOR = 5
    NO_CONN = 6


class BluetoothLE(ble_pb2_grpc.BluetoothLEServicer):
    currentScanResponse = common_pb2.ScanResult(status=common_pb2.Status.STATUS_OK)
    disconnectEvents = []
    notifications = []
    backgroundScan = True
    connections = {}
    scanFilters = {}

    def validate_device(self, request, flags):
        ble = False
        try:
            dev = request.device
            ble = True
        except:
            dev = request

        if VFlags.MAC in flags and not validateMAC(dev.mac):
            return common_pb2.StatusMessage(
                status=common_pb2.Status.STATUS_INVALID_CONNECTION_SETTINGS,
                message="invalid mac addr",
            )

        if VFlags.CONN in flags and dev.mac not in self.connections:
            return common_pb2.StatusMessage(
                status=common_pb2.Status.STATUS_INVALID_CONNECTION_SETTINGS,
                message="device not connected",
            )

        if VFlags.NO_CONN in flags and dev.mac in self.connections:
            return common_pb2.StatusMessage(
                status=common_pb2.Status.STATUS_INVALID_CONNECTION_SETTINGS,
                message="device already connected",
            )

        if ble and VFlags.SERVICE in flags and not validateUUID(request.service.uuid):
            return common_pb2.StatusMessage(
                status=common_pb2.Status.STATUS_INVALID_CONNECTION_SETTINGS,
                message="invalid service UUID",
            )

        if (
            ble
            and VFlags.CHARACTERISTIC in flags
            and not validateUUID(request.characteristic.uuid)
            and request.characteristic.handle == -1
        ):
            return common_pb2.StatusMessage(
                status=common_pb2.Status.STATUS_INVALID_CONNECTION_SETTINGS,
                message="invalid characteristic UUID/handle",
            )

        if (
            ble
            and VFlags.DESCRIPTOR in flags
            and not validateUUID(request.descriptor.uuid)
            and request.descriptor.handle == -1
        ):
            return common_pb2.StatusMessage(
                status=common_pb2.Status.STATUS_INVALID_CONNECTION_SETTINGS,
                message="invalid descriptor UUID/handle",
            )

        return None

    # region BLE Scan
    def configure_scan_filters(self, filters: List[common_pb2.ScanFilter]):
        self.scanFilters = {}
        for i in filters:
            if i.type not in self.scanFilters:
                self.scanFilters[i.type] = []
            self.scanFilters[i.type].append(i.value)

    async def Scan(
        self, request: common_pb2.DeviceScan, context: grpc.aio.ServicerContext
    ) -> common_pb2.ScanResult:
        if not request.avoid_filtering_if_possible:
            self.configure_scan_filters(request.filters)
        async with BleakScanner(
            scanning_mode=("active" if request.active else "passive")
        ) as scanner:
            await asyncio.sleep(request.time)

        resp = common_pb2.ScanResult(status=common_pb2.Status.STATUS_OK)

        for d in scanner.discovered_devices:
            data = {}
            for k,v in d.metadata.get("manufacturer_data").items():
                data[str(k)] = v
            resp.data.append(
                common_pb2.ScanData(
                    device=common_pb2.Device(
                        mac=d.address,
                        type=common_pb2.DeviceType.DEVICE_TYPE_BLE4,
                        name=d.name,
                    ),
                    rssi=d.rssi,
                    manufacturerData=data,
                    time=round(time.time()),
                )
            )
        return resp

    def test_scan_filter_match(self, d):
        if self.scanFilters == {}:
            return True

        k = self.scanFilters.keys()
        if common_pb2.ScanFilterType.SCAN_FILTER_TYPE_MAC in k and d.address in self.scanFilters[common_pb2.ScanFilterType.SCAN_FILTER_TYPE_MAC]:
            return True
        elif common_pb2.ScanFilterType.SCAN_FILTER_TYPE_NAME in k and d.name in self.scanFilters[common_pb2.ScanFilterType.SCAN_FILTER_TYPE_NAME]:
            return True

        return False

    def detection_callback(self, d, advertisement_data):
        if self.test_scan_filter_match(d):
            self.currentScanResponse.data.append(
                common_pb2.ScanData(
                    device=common_pb2.Device(
                        mac=d.address,
                        type=common_pb2.DeviceType.DEVICE_TYPE_BLE4,
                        name=d.name,
                    ),
                    rssi=d.rssi,
                    manufacturer_data=(d.metadata.get("manufacturer_data") or {}).update(
                        advertisement_data.manufacturer_data or {}
                    ),
                    time=round(time.time()),
                )
            )

    async def ScanBackground(self, request: common_pb2.DeviceScan, context):
        if not request.avoid_filtering_if_possible:
            self.configure_scan_filters(request.filters)
        scanner = BleakScanner()
        scanner.register_detection_callback(self.detection_callback)
        await scanner.start()
        while self.backgroundScan:
            await asyncio.sleep(request.time)
            yield self.currentScanResponse
            self.currentScanResponse = common_pb2.ScanResult(
                status=common_pb2.Status.STATUS_OK
            )

    async def ScanBackgroundStop(self, request, context):
        self.backgroundScan = False
        return common_pb2.StatusMessage(status=common_pb2.Status.STATUS_OK)

    # endregion

    # region BLE Connection

    async def Connect(self, request, context):
        v = self.validate_device(request, [VFlags.MAC, VFlags.NO_CONN])
        if v is not None:
            return v

        client = BleakClient(request.mac)
        try:
            await client.connect()
            client.set_disconnected_callback(self.disconnect_callback)
            self.connections[request.mac] = client
        except Exception as e:
            await client.disconnect()
            return common_pb2.StatusMessage(
                status=common_pb2.Status.STATUS_CONNECTION_FAILED, message=str(e)
            )
        return common_pb2.StatusMessage(status=common_pb2.Status.STATUS_OK)

    async def Disconnect(self, request, context):
        v = self.validate_device(request, [VFlags.MAC, VFlags.CONN])
        if v is not None:
            return v
        await self.connections[request.mac].disconnect()
        # removal from array will be handled by disconnect_callback
        return common_pb2.StatusMessage(
            status=common_pb2.Status.STATUS_OK, message="ok"
        )

    def disconnect_callback(self, client):
        if client.address in self.connections:
            del self.connections[client.address]
            self.disconnectEvents.append(
                common_pb2.Device(
                    mac=client.address
                )
            )

    async def ReceiveDisconnect(self, request, context) -> common_pb2.Device:
        while self.disconnectEvents:
            await asyncio.sleep(0.5)
            try:
                yield self.disconnectEvents.pop()
            except:
                pass

    def get_protection_level(self, mode: common_pb2.PairingMode) -> int:
        if mode == common_pb2.PAIRING_MODE_UNK:
            return 0
        elif mode == common_pb2.PAIRING_MODE_ENCRYPTION:
            return 1


    async def Pair(self, request: common_pb2.PairingRequest, context) -> common_pb2.StatusMessage:
        v = self.validate_device(request, [VFlags.MAC])
        if v is not None:
            return v

        try:
            client = self.connections.get(request.mac) or BleakClient(request.mac)
            client.pair(protection_level=self.get_protection_level(request.mode))
            return common_pb2.StatusMessage(
                status=common_pb2.Status.STATUS_OK
            )            
        except Exception as e:
            common_pb2.StatusMessage(
                status=common_pb2.Status.STATUS_ERROR, message=str(e)
            )

    async def Unpair(self, request: common_pb2.Device, context) -> common_pb2.StatusMessage:
        v = self.validate_device(request, [VFlags.MAC])
        if v is not None:
            return v

        try:
            client = self.connections.get(request.mac) or BleakClient(request.mac)
            client.unpair()
            return common_pb2.StatusMessage(
                status=common_pb2.Status.STATUS_OK
            )            
        except Exception as e:
            common_pb2.StatusMessage(
                status=common_pb2.Status.STATUS_ERROR, message=str(e)
            )

    # endregion

    # region helpers

    def get_characteristic_properties(self, properties) -> list:
        props = []
        for j in properties:
            if j == "read":
                props.append(ble_pb2.ChrProperty.CHR_PROPERTY_READ)
            elif j == "write":
                props.append(ble_pb2.ChrProperty.CHR_PROPERTY_WRITE)
            elif j == "notify":
                props.append(ble_pb2.ChrProperty.CHR_PROPERTY_NOTIFY)
            elif j == "broadcast":
                props.append(ble_pb2.ChrProperty.CHR_PROPERTY_BROADCAST)
            elif j == "indicate":
                props.append(ble_pb2.ChrProperty.CHR_PROPERTY_INDICATE)
            elif j == "authenticated-signed-writes":
                props.append(ble_pb2.ChrProperty.CHR_PROPERTY_SIGNED_WRITE)
            elif j == "write-without-response":
                props.append(ble_pb2.ChrProperty.CHR_PROPERTY_WRITE_NO_RESPONSE)
            elif j == "extended-properties":
                props.append(ble_pb2.ChrProperty.CHR_PROPERTY_EXTENDED_PROPS)

        return props

    # endregion


    # region BLE Listings
    async def ListBLEServices(self, request: common_pb2.Device, context) -> ble_pb2.ListBLEServicesResult:
        v = self.validate_device(request, [VFlags.CONN, VFlags.MAC])
        if v is not None:
            return ble_pb2.ListBLEServicesResult(
                status=v
            )

        try:
            s = await self.connections[request.mac].get_services()
        except Exception as e:
            return ble_pb2.ListBLEServicesResult(
                status=common_pb2.StatusMessage(status=common_pb2.STATUS_ERROR, message=str(e)), device=request
            )

        ret = ble_pb2.ListBLEServicesResult(
            status=common_pb2.StatusMessage(status=common_pb2.STATUS_OK), device=request
        )
        for sv in s.services.values():
            chrs = []
            for chr in sv.characteristics:
                descs = []
                for desc in chr.descriptors:
                    descs.append(
                        ble_pb2.BLEDescriptor(
                            uuid=desc.uuid, handle=desc.handle, description=desc.description
                        )
                    )
                chrs.append(
                    ble_pb2.BLECharacteristic(
                    uuid=chr.uuid,
                    descriptors=descs,
                    properties=self.get_characteristic_properties(chr.properties),
                    description=chr.description,
                    handle=chr.handle,
                ))

            ret.data.append(
                ble_pb2.BLEService(
                    uuid=sv.uuid, handle=sv.handle, description=sv.description, characteristics=chrs
                )
            )

        return ret

    async def GetConnectionProperties(self, request: common_pb2.Device, context) -> ble_pb2.BLEConnectionProps:
        v = self.validate_device(request, [VFlags.CONN, VFlags.MAC])
        if v is not None:
            return ble_pb2.BLEConnectionProps(
                status=v, device=request
            )

        dev = self.connections[request.mac]
        rssi = 0
        try:
            rssi = dev.get_rssi()
        except:
            pass
        
        return ble_pb2.BLEConnectionProps(
            status=common_pb2.StatusMessage(status=common_pb2.STATUS_OK), device=request, mtu=dev.mtu_size, rssi=rssi, tx_phy=ble_pb2.PHY_UNK, rx_phy=ble_pb2.PHY_UNK
        )
     
    # endregion

    # region BLE Read/Write

    async def ReadBLECharacteristic(
        self, request: ble_pb2.BLEDevice, context
    ) -> ble_pb2.BLEDataResponse:
        v = self.validate_device(
            request, [VFlags.CONN, VFlags.MAC, VFlags.CHARACTERISTIC]
        )
        if v is not None:
            return ble_pb2.BLEDataResponse(status=v)

        try:
            ret = await self.connections[request.device.mac].read_gatt_char(
                request.characteristic.uuid if request.characteristic.handle < 0 else request.characteristic.handle
            )
        except Exception as e:
            return ble_pb2.BLEDataResponse(
                status=common_pb2.StatusMessage(status=common_pb2.STATUS_ERROR, message=str(e)),
                data=ble_pb2.BLEData(device=request)
            )

        return ble_pb2.BLEDataResponse(
            status=common_pb2.StatusMessage(status=common_pb2.STATUS_OK),
            data=ble_pb2.BLEData(device=request, data=bytes(ret))
        )

    async def WriteBLECharacteristic(
        self, request: ble_pb2.BLEDataWrite, context
    ) -> common_pb2.StatusMessage:
        v = self.validate_device(
            request.data.device, [VFlags.CONN, VFlags.MAC, VFlags.CHARACTERISTIC]
        )
        if v is not None:
            return v

        try:
            await self.connections[request.data.device.device.mac].write_gatt_char(
                request.data.device.characteristic.uuid if request.data.device.characteristic.handle < 0 else request.data.device.characteristic.handle, request.data.data, (False if request.mode == ble_pb2.WRITE_MODE_NO_RESPONSE else True)
            )
        except Exception as e:
            return common_pb2.StatusMessage(
                status=common_pb2.Status.STATUS_UNK, message=str(e)
            )
            
        return common_pb2.StatusMessage(
            status=common_pb2.Status.STATUS_OK, message="ok"
        )

    async def ReadBLEDescriptor(
        self, request: ble_pb2.BLEDevice, context
    ) -> ble_pb2.BLEDataResponse:
        v = self.validate_device(request, [VFlags.CONN, VFlags.MAC, VFlags.DESCRIPTOR])
        if v is not None:
            return ble_pb2.BLEDataResponse(status=v)

        try:
            ret = await self.connections[request.device.mac].read_gatt_descriptor(
                request.device.descriptor.handle
            )
        except Exception as e:
            return ble_pb2.BLEDataResponse(
                status=common_pb2.StatusMessage(status=common_pb2.STATUS_ERROR, message=str(e)),
                data=ble_pb2.BLEData(device=request.device)
            )

        return ble_pb2.BLEDataResponse(
            status=common_pb2.StatusMessage(status=common_pb2.STATUS_OK),
            data=ble_pb2.BLEData(device=request, data=bytes(ret))
        )

    async def WriteBLEDescriptor(
        self, request: ble_pb2.BLEDataWrite, context
    ) -> common_pb2.StatusMessage:
        v = self.validate_device(
            request.data.device, [VFlags.CONN, VFlags.MAC, VFlags.CHARACTERISTIC]
        )
        if v is not None:
            return v

        try:
            await self.connections[request.data.device.device.mac].write_gatt_descriptor(
                request.data.device.descriptor.handle, request.data.data
            )
        except Exception as e:
            return common_pb2.StatusMessage(
                status=common_pb2.Status.STATUS_UNK, message=str(e)
            )

        return common_pb2.StatusMessage(
            status=common_pb2.Status.STATUS_OK, message="ok"
        )

    # endregion

    # region BLE Notifications

    async def Subscribe(
        self, request: ble_pb2.BLEDevice, context
    ) -> common_pb2.StatusMessage:
        v = self.validate_device(
            request, [VFlags.CONN, VFlags.MAC, VFlags.CHARACTERISTIC]
        )
        if v is not None:
            return v

        self.connections[request.device.mac].start_notify(
            request.characteristic.uuid, partial(self.notification_callback, request)
        )

        self.notificationSubscriptions[request.device.mac].append(
            request.characteristic.uuid
        )

        return common_pb2.StatusMessage(
            status=common_pb2.Status.STATUS_OK, message="ok"
        )

    def notification_callback(self, device: ble_pb2.BLEDevice, sender: int, data: bytearray):
        self.notifications.append(
            ble_pb2.BLEDataResponse(
                status=common_pb2.StatusMessage(status=common_pb2.STATUS_OK),
                data=ble_pb2.BLEData(
                    device=ble_pb2.BLEDevice(
                        status=device.status,
                        device=device.device,
                        service=device.service,
                        characteristic=ble_pb2.BLECharacteristic(uuid=device.characteristic.uuid, handle=sender)
                    ),
                    data=data,
                )
            )
        )

    async def Unsubscribe(
        self, request: ble_pb2.BLEDevice, context
    ) -> common_pb2.StatusMessage:
        v = self.validate_device(
            request, [VFlags.CONN, VFlags.MAC, VFlags.CHARACTERISTIC]
        )
        if v is not None:
            return v
        self.connections[request.device.mac].stop_notify(request.characteristic.uuid)
        return common_pb2.StatusMessage(
            status=common_pb2.Status.STATUS_OK, message="ok"
        )

    async def ReceiveNotifications(self, request, context) -> ble_pb2.BLEDataResponse:
        while self.notifications:
            await asyncio.sleep(0.5)
            try:
                yield self.notifications.pop()
            except:
                pass

    # endregion


