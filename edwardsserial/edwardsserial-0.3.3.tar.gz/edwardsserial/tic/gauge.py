import re
import warnings

from edwardsserial.serial_protocol import SerialProtocol


class Gauge(SerialProtocol):
    GAUGE_NAME = re.compile(
        "[A-Z0-9]{0,4}$"
    )  # [a-z] does not get an error response but does not change the name.
    UNITS = {
        59: "Pa",
        66: "V",
        81: "%",
    }

    GAUGE_TYPE = {
        0: "Unknown Device",
        1: "No Device",
        2: "EXP_CM",
        3: "EXP_STD",
        4: "CMAN_S",
        5: "CMAN_D",
        6: "TURBO",
        7: "APGM",
        8: "APGL",
        9: "APGXM",
        10: "APGXH",
        11: "APGXL",
        12: "ATCA",
        13: "ATCD",
        14: "ATCM",
        15: "WRG",
        16: "AIMC",
        17: "AIMN",
        18: "AIMS",
        19: "AIMX",
        20: "AIGC_I2R",
        21: "AIGX_2FIL",
        22: "ION_EB",
        23: "AIGXS",
        24: "USER",
        25: "ASG",
    }

    GAUGE_STATE = {
        0: "Gauge Not Connected",
        1: "Gauge Connected",
        2: "New Gauge ID",
        3: "Gauge Change",
        4: "Gauge In ALert",
        5: "Off",
        6: "Striking",
        7: "Initialising",
        8: "Calibrate",
        9: "Zeroing",
        10: "Degassing",
        11: "On",
        12: "Inhibited",
    }

    GAS_TYPE = {
        0: "Nitrogen",
        1: "Helium",
        2: "Argon",
        3: "Carbon Dioxide",
        4: "Neon",
        5: "Krypton",
        6: "Voltage",
    }

    ASG_RANGE = {
        0: "1000 mbar",
        1: "2000 mbar",
    }

    def __init__(self, port, object_id):
        super().__init__(port)
        self.OBJECT_ID = object_id

    @property
    def pressure(self):
        value, unit, state = self._check_alert(self.OBJECT_ID)
        if int(state) not in [8, 11]:
            return None
        unit = int(unit)
        if unit == 81:
            return int(value)
        return float(value)

    @property
    def unit(self):
        value, unit, state = self._check_alert(self.OBJECT_ID)
        return self.UNITS.get(int(unit))

    @property
    def state(self):
        value, unit, state = self._check_alert(self.OBJECT_ID)
        return f"{state}: {self.GAUGE_STATE.get(int(state))}"

    @property
    def type(self):
        config_type, gauge_type = self.send_message("?S", self.OBJECT_ID, 5)
        return f"{gauge_type}: {self.GAUGE_TYPE.get(int(gauge_type))}"

    @property
    def name(self):
        config_type, name = self.send_message("?S", self.OBJECT_ID, 68)
        return name

    @name.setter
    def name(self, value):
        if not self.GAUGE_NAME.match(value):
            raise ValueError(
                "Wrong name format: Only 4 characters of [A-Z0-9] are allowed."
            )
        self.send_message("!S", self.OBJECT_ID, f"68;{value}")

    @property
    def gas_type(self):
        config_type, gas_type, gas_filter = self.send_message("?S", self.OBJECT_ID, 7)
        return f"{gas_type}: {self.GAS_TYPE.get(int(gas_type))}"

    @gas_type.setter
    def gas_type(self, value):
        if value not in self.GAS_TYPE.keys():
            raise ValueError(f"Value must be a key from {self.GAS_TYPE}")
        self.send_message("!S", self.OBJECT_ID, f"7;{value};{int(self.filter)}")

    @property
    def filter(self):
        """Moving average filter for the pressure of 1 second.

        Returns
        -------
        Filter active: True or False
        """
        config_type, gas_type, gas_filter = self.send_message("?S", self.OBJECT_ID, 7)
        return bool(int(gas_filter))

    @filter.setter
    def filter(self, value: bool):
        if not isinstance(value, bool):
            raise ValueError(f"Value must be boolean.")
        self.send_message("!S", self.OBJECT_ID, f"7;{self.gas_type[0]};{int(value)}")

    @property
    def ASG_range(self):
        config_type, asg_range = self.send_message("!S", self.OBJECT_ID, 6)
        return f"{int(asg_range)}: {self.ASG_RANGE.get(int(asg_range))}"

    @ASG_range.setter
    def ASG_range(self, value):
        if value not in self.ASG_RANGE.keys():
            raise ValueError(f"Value must be a key from {self.ASG_RANGE}")
        self.send_message("!S", self.OBJECT_ID, f"{6};{value}")

    def on(self):
        self.send_message("!C", self.OBJECT_ID, 1)

    def off(self):
        self.send_message("!C", self.OBJECT_ID, 0)

    def zero(self):
        self.send_message("!C", self.OBJECT_ID, 3)

    def calibrate(self):
        self.send_message("!C", self.OBJECT_ID, 4)

    def degas(self):
        self.send_message("!C", self.OBJECT_ID, 5)

    def new_id(self):
        self.send_message("!C", self.OBJECT_ID, 2)
