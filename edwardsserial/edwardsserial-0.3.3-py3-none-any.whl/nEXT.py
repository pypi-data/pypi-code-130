from edwardsserial.descriptors import SerialQuery, ValueRange
from edwardsserial.serial_protocol import SerialProtocol


# make this as a descriptor that calls the owners pump start methods if available,
# since TIC does not forward some commands
class nEXT(SerialProtocol):
    """
    Test Docstring
    """

    timer = ValueRange(start=1, end=30, operation="S", object_id=854)
    power_limit = ValueRange(start=50, end=200, operation="S", object_id=855)
    normal_speed = ValueRange(start=50, end=100, operation="S", object_id=856)
    standby_speed = ValueRange(start=55, end=100, operation="S", object_id=857)

    PIC_software_version = SerialQuery("S", 868, data_type=str)

    controller_run_time = SerialQuery("V", 882, data_type=int)
    pump_run_time = SerialQuery("V", 883, data_type=int)
    cycles = SerialQuery("V", 884, data_type=int)
    bearing_run_time = SerialQuery("V", 885, data_type=int)
    oil_cartridge_run_time = SerialQuery("V", 886, data_type=int)

    def restore_factory_settings(self):
        self.send_message("!S", 867, 1)

    @property
    def link_voltage(self):
        """Measured link voltage in V"""
        ret_val = 0.1 * self.send_message("?V", 860)[0]
        return ret_val

    @property
    def link_current(self):
        """Measured link current in A"""
        ret_val = 0.1 * self.send_message("?V", 860)[1]
        return ret_val

    @property
    def link_power(self):
        """Measured link power in W"""
        ret_val = 0.1 * self.send_message("?V", 860)[2]
        return ret_val

    @property
    def motor_temperature(self):
        """Motor temperature in \u00B0C"""
        ret_val = int(self.send_message("?V", 859)[0])
        return ret_val

    @property
    def controller_temperature(self):
        """Controller temperature in \u00B0C"""
        ret_val = int(self.send_message("?V", 859)[1])
        return ret_val
