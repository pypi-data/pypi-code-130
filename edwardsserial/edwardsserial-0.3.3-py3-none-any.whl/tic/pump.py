from abc import ABC, abstractmethod

from edwardsserial.serial_protocol import SerialProtocol


class Pump(SerialProtocol, ABC):
    PUMP_ID: int
    SPEED_ID: int
    POWER_ID: int

    PUMP_STATE = {
        0: "Stopped",
        1: "Starting Delay",
        2: "Stopping Short Delay",
        3: "Stopping Normal Delay",
        4: "Running",
        5: "Accelerating",
        6: "Fault Braking",
        7: "Braking",
    }
    PUMP_TYPE = {
        0: "No Pump",
        1: "EXDC",
        3: "EXT75DX",
        4: "EXT255DC",
        8: "Mains Backing Pump",
        9: "Serial Pump",
        10: "nEXT - 485",
        11: "nEXT - 232",
        12: "nXDS",
        # 16: "nEXT",  # todo: check if this is True
        99: "Not yet identified",
    }

    def on(self):
        self.send_message("!C", self.PUMP_ID, 1)

    def off(self):
        self.send_message("!C", self.PUMP_ID, 0)

    @property
    def state(self):
        state = int(*self._check_alert(self.PUMP_ID))
        return f"{state}: {self.PUMP_STATE.get(state)}"

    @property
    def speed(self):
        return float(*self._check_alert(self.SPEED_ID))

    @property
    def power(self):
        return float(*self._check_alert(self.POWER_ID))

    @property
    def type(self):
        config_type, pump_type = self.send_message("?S", self.PUMP_ID, 3)
        return f"{pump_type}: {self.PUMP_TYPE.get(int(pump_type))}"


class TurboPump(Pump):
    PUMP_ID = 904
    SPEED_ID = 905
    POWER_ID = 906
    NORMAL_ID = 907
    STANDBY_ID = 908
    CYCLE_ID = 909

    @property
    def normal(self):
        value = int(*self._check_alert(self.NORMAL_ID))
        if value == 0:
            return False
        if value == 4:
            return True
        raise ValueError(f"Got state={value}. Expected 0 or 4.")

    @property
    def standby(self):
        value = int(*self._check_alert(self.STANDBY_ID))
        if value == 0:
            return False
        if value == 4:
            return True
        raise ValueError(f"Got state={value}. Expected 0 or 4.")

    @standby.setter
    def standby(self, value: bool):
        if not isinstance(value, bool):
            raise TypeError("Value must be of type bool.")
        self.send_message("?C", self.STANDBY_ID, int(value))

    @property
    def cycle_time(self):
        value, state = self._check_alert(self.CYCLE_ID)
        return int(value)

    @property
    def delay(self):
        config_type, delay = self.send_message("?S", self.PUMP_ID, 21)
        return int(delay)

    @delay.setter
    def delay(self, value: int):
        if value not in range(0, 100):
            raise ValueError("Must be between 0 and 99")
        self.send_message("!S", self.PUMP_ID, f"21;{value}")


class BackingPump(Pump):
    PUMP_ID = 910
    SPEED_ID = 911
    POWER_ID = 912

    @property
    def sequence_options(self):
        pass
