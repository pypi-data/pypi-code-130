from edwardsserial.serial_protocol import SerialProtocol
from edwardsserial.tic.gauge import Gauge
from edwardsserial.tic.pump import BackingPump, TurboPump


class TIC(SerialProtocol):
    def __init__(self, port):
        super().__init__(port)
        self._turbo_pump = TurboPump(port)
        self._backing_pump = BackingPump(port)
        self._gauge1 = Gauge(port, 913)
        self._gauge2 = Gauge(port, 914)
        self._gauge3 = Gauge(port, 915)

    PRESSURE_UNITS = {
        1: "kPa",
        2: "mbar",
        3: "Torr",
    }

    @property
    def turbo_pump(self):
        return self._turbo_pump

    @property
    def backing_pump(self):
        return self._backing_pump

    @property
    def gauge1(self):
        return self._gauge1

    @property
    def gauge2(self):
        return self._gauge2

    @property
    def gauge3(self):
        return self._gauge3

    @property
    def gauge_values(self):
        answer = self.send_message("?V", 940)
        values = {
            int(gauge): float(value) for gauge, value in zip(answer[::2], answer[1::2])
        }
        return values

    @property
    def status(self):
        state = self._check_alert(933)
        return f"{state}: {self.STATE[state]}"

    @property
    def pressure_units(self):
        unit = self.send_message("?S", 929)
        return f"{unit}: {self.PRESSURE_UNITS.get(unit)}"

    @pressure_units.setter
    def pressure_units(self, value):
        if value not in self.PRESSURE_UNITS.keys():
            raise ValueError(f"Value must be a key from {self.PRESSURE_UNITS}")
        self.send_message("!S", 929, value)

    @property
    def display_contrast(self):
        return int(self.send_message("?S", 925))

    @display_contrast.setter
    def display_contrast(self, value):
        if value not in range(-5, 16):
            raise ValueError(f"Value must be in {range(-5,16)}")
        self.send_message("!S", 925, value)

    @property
    def internal_temperature(self):
        temperature = self._check_alert(920)
        return float(temperature)

    @property
    def power_supply_temperature(self):
        temperature = self._check_alert(919)
        return float(temperature)
