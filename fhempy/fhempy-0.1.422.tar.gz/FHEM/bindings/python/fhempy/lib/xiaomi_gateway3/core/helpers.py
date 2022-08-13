import logging
from dataclasses import dataclass, field
from typing import *

from .utils import DOMAIN

from . import bluetooth, zigbee

CONNECTION_NETWORK_MAC = "mac"

_LOGGER = logging.getLogger(__name__)


# TODO: rewrite all usage to dataclass
@dataclass
class XiaomiDevice:
    did: str  # unique Xiaomi did
    model: str  # Xiaomi model
    mac: str
    type: str  # gateway, zigbee, ble, mesh
    online: bool

    lumi_spec: list
    miot_spec: list

    device_info: Dict[str, Any]

    stats: "XiaomiEntity"

    extra: Dict[str, Any] = field(default_factory=dict)

    # all device entities except stats
    entities: Dict[str, "XiaomiEntity"] = field(default_factory=dict)

    gateways: List["Gateway3"] = field(default_factory=list)


class DevicesRegistry:
    """Global registry for all gateway devices. Because BLE devices updates
    from all gateway simultaniosly.

    Key - device did, `numb` for wifi and mesh devices, `lumi.ieee` for zigbee
    devices, `blt.3.alphanum` for ble devices, `group.numb` for mesh groups.
    """

    devices: Dict[str, dict] = {}
    setups: Dict[str, Callable] = None

    defaults: Dict[str, dict] = {}

    def add_setup(self, domain: str, handler):
        """Add hass device setup funcion."""
        self.setups[domain] = handler

    async def add_entity(self, domain: str, device: dict, attr: str):
        if self not in device["gateways"]:
            device["gateways"].append(self)

        if domain is None or attr in device["entities"]:
            return

        # instant add entity to prevent double setup
        device["entities"]["main"] = None

        if domain in self.setups:
            await self.setups[domain](self, device, attr)

    def set_entity(self, fhem_dev):
        fhem_dev.device["entities"]["main"] = fhem_dev

    def remove_entity(self, fhem_dev):
        fhem_dev.device["entities"].pop("main")

    def add_stats(self, device: dict):
        if "stats" in device:
            return

        device["stats"] = None

        self.setups["sensor"](self, device, device["type"])

    def set_stats(self, fhem_dev):
        fhem_dev.device["stats"] = fhem_dev

    def remove_stats(self, fhem_dev):
        fhem_dev.device.pop("stats")

    def find_or_create_device(self, device: dict) -> dict:
        type_ = device["type"]
        did = device["did"] if type_ != "ble" else device["mac"].lower()
        if did in self.devices:
            return self.devices[did]

        self.devices[did] = device

        # update device with specs
        if type_ in ("gateway", "zigbee"):
            device.update(zigbee.get_device(device["model"]))
        elif type_ == "mesh":
            device.update(bluetooth.get_device(device["model"], "Mesh"))
        elif type_ == "ble":
            device.update(bluetooth.get_device(device["model"], "BLE"))

        model = device["model"]
        if model in self.defaults:
            device.update(self.defaults[model])

        if did in self.defaults:
            device.update(self.defaults[did])

        mac = device["mac"].lower()
        if did != mac and mac in self.defaults:
            device.update(self.defaults[mac])

        device["entities"] = {}
        device["gateways"] = []

        return device


class XiaomiEntity:
    _ignore_offline = None
    _state = None

    def __init__(self, gateway: "Gateway3", device: dict, attr: str):
        self.gw = gateway
        self.device = device

        self.attr = attr
        self._attrs = {}

        self._unique_id = f"{device.get('entity_name', device['mac'])}_{attr}"
        self._name = device["device_name"] + " " + attr.replace("_", " ").title()

        self.entity_id = f"{DOMAIN}.{self._unique_id}"

    def debug(self, message: str):
        self.gw.debug(f"{self.entity_id} | {message}")

    # @property
    # def entity_registry_enabled_default(self):
    #     return False

    @property
    def should_poll(self) -> bool:
        return False

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def name(self):
        return self._name

    @property
    def available(self) -> bool:
        gw_available = any(gateway.available for gateway in self.device["gateways"])
        return gw_available and (
            self.device.get("online", True) or self._ignore_offline
        )

    @property
    def device_state_attributes(self):
        return self._attrs

    @property
    def device_info(self):
        """
        https://developers.home-assistant.io/docs/device_registry_index/
        """
        type_ = self.device["type"]
        if type_ == "gateway":
            return {
                "connections": {(CONNECTION_NETWORK_MAC, self.device["wlan_mac"])},
                "identifiers": {(DOMAIN, self.device["mac"])},
                "manufacturer": self.device["device_manufacturer"],
                "model": self.device["device_model"],
                "name": self.device["device_name"],
                "sw_version": self.device["fw_ver"],
            }
        elif type_ == "zigbee":
            return {
                "connections": {(type_, self.device["mac"])},
                "identifiers": {(DOMAIN, self.device["mac"])},
                "manufacturer": self.device.get("device_manufacturer"),
                "model": self.device["device_model"],
                "name": self.device["device_name"],
                "sw_version": self.device["fw_ver"],
                "via_device": (DOMAIN, self.gw.device["mac"]),
            }
        else:  # ble and mesh
            return {
                "connections": {("bluetooth", self.device["mac"])},
                "identifiers": {(DOMAIN, self.device["mac"])},
                "manufacturer": self.device.get("device_manufacturer"),
                "model": self.device["device_model"],
                "name": self.device["device_name"],
                "via_device": (DOMAIN, self.gw.device["mac"]),
            }

    async def async_update(self, data: dict):
        raise NotImplementedError
