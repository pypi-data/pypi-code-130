"""Messages to send to the device.

This module provides dataclass objects that act as templates for you to
'fill in' with data. This allows you to focus on WHAT to send, not how.

Some commands will have an extra ``response_cls`` attribute. This
attribute is used internally in the library, but may be useful for you.
It holds the response type, not the actual device response.

All commands that control automatic reporting of the device's internal
state changes have an extra ``callback`` attribute. This attribute is a
shortcut to automatically register a callback to handle incoming
responses from the device.
"""


from dataclasses import asdict, dataclass, field
from typing import Callable, Optional, Tuple

from pythonosc.osc_message import OscMessage
from pythonosc.osc_message_builder import OscMessageBuilder

from stepseries import responses


@dataclass
class OSCCommand(object):
    """An abstract class meant to be implemented by OSC command objects.

    If implementing your own command, it must inherit this class.
    """

    def build(self) -> OscMessage:
        """Converts the builder to a usable OSC message."""
        # Convert the builder to a dictionary
        builder_dict = asdict(self)

        # Extract the values
        # Code is largely copy-paste from pythonosc.UDPClient
        address = builder_dict.pop("address")
        builder_dict.pop("callback", None)
        builder_dict.pop("response_cls", None)

        builder = OscMessageBuilder(address=address)

        # Return as a message string
        for v in builder_dict.values():
            if isinstance(v, bool):
                v = int(v)
            builder.add_arg(v)

        return builder.build()

    def stringify(self) -> str:
        """Converts the builder to an OSC message string."""
        # Convert the builder to a dictionary
        builder_dict = asdict(self)
        builder_dict.pop("callback", None)
        builder_dict.pop("response_cls", None)

        # Extract the values
        address: str = builder_dict.pop("address") + " "

        # Return as a message string
        for v in builder_dict.values():
            if isinstance(v, bool):
                v = int(v)
            if v is None:
                continue
            address += str(v) + " "

        return address[:-1]


@dataclass
class OSCSetCommand(OSCCommand):
    """A command that only performs set functions on the device."""


@dataclass
class OSCGetCommand(OSCCommand):
    """A command that only performs get functions on the device."""


# System Settings


@dataclass
class SetDestIP(OSCGetCommand):
    """Set the destination IP address for the device's responses.

    Query replies, internal state reports, or command errors are sent to
    this destination IP. Typically this is the IP address of your
    computer. Upon receipt, the device will reply with a
    :py:class:`stepseries.responses.DestIP`. object.

    Until this command is sent, no OSC messages will be sent from the
    device with the exception being ``responses.Booted``. The
    `Config Tool`_ allows you to configure whether the device should
    wait for this command.

    Note: The library will return before
    :py:class:`stepseries.responses.DestIP` is received. This behavior
    will be changed in a future update.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+

    .. _Config Tool: http://ponoor.com/tools/step400-config/
    """

    address: str = field(default="/setDestIp", init=False)
    response_cls: responses.DestIP = field(default=responses.DestIP, init=False)


@dataclass
class GetVersion(OSCGetCommand):
    """Retrieve the current firmware version of the controller.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/getVersion", init=False)
    response_cls: responses.Version = field(default=responses.Version, init=False)


@dataclass
class GetConfigName(OSCGetCommand):
    """Retrieve the name of the microSD config file on the controller.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/getConfigName", init=False)
    response_cls: responses.ConfigName = field(default=responses.ConfigName, init=False)


@dataclass
class ReportError(OSCSetCommand):
    """Enable or disable automatic reports for command errors.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/reportError", init=False)
    response_cls: Tuple[responses.ErrorCommand, responses.ErrorOSC] = field(
        default_factory=lambda: (responses.ErrorCommand, responses.ErrorOSC),
        init=False,
    )
    enable: bool
    """If True, enable the reporting.

    +-------+-----+
    |Default|False|
    +-------+-----+
    """
    callback: Optional[Callable[..., None]] = None


@dataclass
class ResetDevice(OSCSetCommand):
    """Resets the entire device.

    A programmatic version of physically pressing the RESET button.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/resetDevice", init=False)
    response_cls: responses.Booted = field(default=responses.Booted, init=False)


# Motor Driver Settings


@dataclass
class SetMicrostepMode(OSCSetCommand):
    """Sets the microstepping mode.

    Voltage mode allows microstepping up to 1/128 which is also the
    default. Current mode only allows microstepping up to 1/16.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/setMicrostepMode", init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """
    STEP_SEL: int
    """
    The microstep mode to run the motor at.

    +--------+-------------------------+
    |STEP_SEL|Mode Description         |
    +--------+-------------------------+
    |0       |1/1 microstep (full-step)|
    +--------+-------------------------+
    |1       |1/2 microstep            |
    +--------+-------------------------+
    |2       |1/4 microstep            |
    +--------+-------------------------+
    |3       |1/8 microstep            |
    +--------+-------------------------+
    |4       |1/16 microstep           |
    +--------+-------------------------+
    |5       |1/32 microstep           |
    +--------+-------------------------+
    |6       |1/64 microstep           |
    +--------+-------------------------+
    |7       |1/128 microstep          |
    +--------+-------------------------+

    +-------+---------------+
    |Default|1/128 microstep|
    +-------+---------------+
    """


@dataclass
class GetMicrostepMode(OSCGetCommand):
    """Retrieves the configured microstepping mode for a motor.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/getMicrostepMode", init=False)
    response_cls: responses.MicrostepMode = field(
        default=responses.MicrostepMode, init=False
    )
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """


@dataclass
class EnableLowSpeedOptimize(OSCSetCommand):
    """Enable or disable low speed optimization.

    At very low speeds with minimal drive voltage, motors tend to have
    difficulty maintaining smooth operation due to phase current
    distortion. This optimizer attempts to compensate for that. When
    enabled, the minimum speed of the speed profile is forced to zero.

    See the datasheet for more details.

    +-----------------+-------+
    |Executable Timing|Stopped|
    +-----------------+-------+
    """

    address: str = field(default="/enableLowSpeedOptimize", init=False)
    response_cls: responses.LowSpeedOptimizeThreshold = field(
        default=responses.LowSpeedOptimizeThreshold, init=False
    )
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """
    enable: bool
    """If True, enable the optimizer.

    +-------+-----+
    |Default|False|
    +-------+-----+
    """


@dataclass
class SetLowSpeedOptimizeThreshold(OSCSetCommand):
    """Set the threshold for phase current distortion compensation.

    At very low speeds with minimal drive voltage, motors tend to have
    difficulty maintaining smooth operation due to phase current
    distortion. This optimizer attempts to compensate for that.

    .. note:: Make sure to enable this optimizer with
        :py:class:`stepseries.commands.EnableLowSpeedOptimize`.

    +-----------------+----------------+
    |Executable Timing|Motor is stopped|
    +-----------------+----------------+
    """

    address: str = field(default="/setLowSpeedOptimizeThreshold", init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """
    lowSpeedOptimizationThreshold: float
    """
    +-----------+---------------------+
    |Valid Range|0.0 - 976.3 [steps/s]|
    +-----------+---------------------+
    |Default    |0 [steps/s]          |
    +-----------+---------------------+
    """


@dataclass
class GetLowSpeedOptimizeThreshold(OSCGetCommand):
    """Retrieve the low speed optimization threshold.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/getLowSpeedOptimizeThreshold", init=False)
    response_cls: responses.LowSpeedOptimizeThreshold = field(
        default=responses.LowSpeedOptimizeThreshold, init=False
    )
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """


@dataclass
class EnableBusyReport(OSCSetCommand):
    """Enable or disable the automatic reporting of busy status changes.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/enableBusyReport", init=False)
    response_cls: responses.Busy = field(default=responses.Busy, init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """
    enable: bool
    """If True, enable the reporting.

    +-------+-----+
    |Default|False|
    +-------+-----+
    """
    callback: Optional[Callable[..., None]] = None


@dataclass
class GetBusy(OSCGetCommand):
    """Retrieve the busy status of a motor.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/getBusy", init=False)
    response_cls: responses.Busy = field(default=responses.Busy, init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """


@dataclass
class EnableHiZReport(OSCSetCommand):
    """Enable or disable the automatic reporting of HiZ status changes.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/enableHizReport", init=False)
    response_cls: responses.HiZ = field(default=responses.HiZ, init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """
    enable: bool
    """If True, enable the reporting.

    +-------+-----+
    |Default|False|
    +-------+-----+
    """
    callback: Optional[Callable[..., None]] = None


@dataclass
class GetHiZ(OSCGetCommand):
    """Retrieve the HiZ status of a motor.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/getHiZ", init=False)
    response_cls: responses.HiZ = field(default=responses.HiZ, init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """


@dataclass
class EnableDirReport(OSCSetCommand):
    """Enable or disable the automatic reporting of direction changes.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/enableDirReport", init=False)
    response_cls: responses.Dir = field(default=responses.Dir, init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """
    enable: bool
    """If True, enable the reporting.

    +-------+-----+
    |Default|False|
    +-------+-----+
    """
    callback: Optional[Callable[..., None]] = None


@dataclass
class GetDir(OSCGetCommand):
    """Retrieve the current direction of a motor.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/getDir", init=False)
    response_cls: responses.Dir = field(default=responses.Dir, init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """


@dataclass
class EnableMotorStatusReport(OSCSetCommand):
    """Enable or disable the automatic reporting of motor op changes.

    The reports are sent when the motor changes its current op like
    acceleration, constant speed, deceleration or stopping.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/enableMotorStatusReport", init=False)
    response_cls: responses.MotorStatus = field(
        default=responses.MotorStatus, init=False
    )
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """
    enable: bool
    """If True, enable the reporting.

    +-------+-----+
    |Default|False|
    +-------+-----+
    """
    callback: Optional[Callable[..., None]] = None


@dataclass
class GetMotorStatus(OSCGetCommand):
    """Retrieve the current op status of a motor.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/getMotorStatus", init=False)
    response_cls: responses.MotorStatus = field(
        default=responses.MotorStatus, init=False
    )
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """


@dataclass
class SetPositionReportInterval(OSCSetCommand):
    """Periodically send the current position of a motor.

    When enabled,
    :py:class:`stepseries.commands.SetPositionListReportInterval` will
    be disabled.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/setPositionReportInterval", init=False)
    response_cls: responses.Position = field(default=responses.Position, init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """
    interval: int
    """Time interval between reports.

    When set to 0, this reporting is disabled.

    +-----------+---------------------+
    |Valid Range|0-2147483647 [ms]    |
    +-----------+---------------------+
    |Default    |0 [ms]               |
    +-----------+---------------------+
    """
    callback: Optional[Callable[..., None]] = None


@dataclass
class SetPositionListReportInterval(OSCSetCommand):
    """Periodically send the current positions of all motors.

    When enabled,
    :py:class:`stepseries.commands.SetPositionReportInterval` will
    be disabled.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/setPositionListReportInterval", init=False)
    response_cls: responses.PositionList = field(
        default=responses.PositionList, init=False
    )
    interval: int
    """Time interval between reports.

    When set to 0, this reporting is disabled.

    +-----------+-----------------+
    |Valid Range|0-2147483647 [ms]|
    +-----------+-----------------+
    |Default    |0 [ms]           |
    +-----------+-----------------+
    """
    callback: Optional[Callable[..., None]] = None


@dataclass
class GetAdcVal(OSCGetCommand):
    """Retrieves ``ADC_OUT`` register values for a motor.

    ``ADC_OUT`` stores the 5-bit AD-converted voltage reading from the
    ADC pin on the motor driver chip. In the STEP400, this pin is pulled
    up with a 10kΩ resistor wired directly to the LIMITSW connector. In
    the STEP800, this pin is tied to GND and will always be 0V.

    .. note:: This command is only meant for debugging purposes. Most
        users should avoid this command.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/getAdcVal", init=False)
    response_cls: responses.AdcVal = field(default=responses.AdcVal, init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    """


@dataclass
class GetStatus(OSCGetCommand):
    """Retrieves the status of the motor driver chip on the device.

    This status includes the op status of the motor, alarms and,
    switches.

    .. note:: This command is only meant for debugging purposes. Most
        users should avoid this command.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/getStatus", init=False)
    response_cls: responses.Status = field(default=responses.Status, init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """


@dataclass
class GetConfigRegister(OSCGetCommand):
    """Retrieves the CONFIG register values for a motor.

    This register stores information about motor, alaram, and switch
    statuses.

    .. note:: This command is only meant for debugging purposes. Most
        users should avoid this command.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/getConfigRegister", init=False)
    response_cls: responses.ConfigRegister = field(
        default=responses.ConfigRegister, init=False
    )
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """


@dataclass
class ResetMotorDriver(OSCSetCommand):
    """Resets the specified motor driver chip and resets defaults.

    .. note:: This command is only meant for debugging purposes. Most
        users should avoid this command.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+

    ``Deprecated``
    """

    address: str = field(default="/resetMotorDriver", init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """


# Alarm Settings


@dataclass
class EnableUvloReport(OSCSetCommand):
    """Enable or disable the automatic reporting of undervoltage events.

    Undervoltage lockouts (UVLO) occur when the voltage supply to the
    motor falls below the UVLO turn-off threshold. In this state, the
    motor cannot be operated. UVLO will be reset when the voltage supply
    again rises above that threshold.

    This report is enabled by default.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/enableUvloReport", init=False)
    response_cls: responses.Uvlo = field(default=responses.Uvlo, init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """
    enable: bool
    """If True, enable the reporting.

    +-------+----+
    |Default|True|
    +-------+----+
    """
    callback: Optional[Callable[..., None]] = None


@dataclass
class GetUvlo(OSCGetCommand):
    """Retrieves the current state of UVLO.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/getUvlo", init=False)
    response_cls: responses.Uvlo = field(default=responses.Uvlo, init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """


@dataclass
class EnableThermalStatusReport(OSCSetCommand):
    """Enable or disable the automatic reporting of thermal statuses.

    Thermal status events are sent whenever the motor driver exceeds
    certain temperature thresholds. Note that these thresholds are
    different between the STEP400 and STEP800.

    Two thresholds will automatically shut down the driver or device
    when crossed and the corresponding motor(s) will be placed into a
    HiZ state with or without notification. It is HIGHLY recommended to
    put the included heatsinks on each motor driver chip to avoid
    hitting these thermal thresholds.

    This report is enabled by default.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+

    **STEP400:**

    +---------+---------------+----------------+-----------------+
    |TH_STATUS|Description    |Enable Threshold|Disable Threshold|
    +---------+---------------+----------------+-----------------+
    |0        |Normal         |-               |-                |
    +---------+---------------+----------------+-----------------+
    |1        |Warning        |135°C           |125°C            |
    +---------+---------------+----------------+-----------------+
    |2        |Bridge shutdown|155°C           |145°C            |
    +---------+---------------+----------------+-----------------+
    |3        |Device shutdown|170°C           |130°C            |
    +---------+---------------+----------------+-----------------+

    **STEP800:**

    +---------+---------------+----------------+-----------------+
    |TH_STATUS|Description    |Enable Threshold|Disable Threshold|
    +---------+---------------+----------------+-----------------+
    |0        |Normal         |-               |-                |
    +---------+---------------+----------------+-----------------+
    |1        |Warning        |130°C           |130°C            |
    +---------+---------------+----------------+-----------------+
    |2        |Bridge shutdown|160°C           |130°C            |
    +---------+---------------+----------------+-----------------+
    """

    address: str = field(default="/enableThermalStatusReport", init=False)
    response_cls: responses.ThermalStatus = field(
        default=responses.ThermalStatus, init=False
    )
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """
    enable: bool
    """If True, enable the reporting.

    +-------+----+
    |Default|True|
    +-------+----+
    """
    callback: Optional[Callable[..., None]] = None


@dataclass
class GetThermalStatus(OSCGetCommand):
    """Retrieves the thermal status of motor.

    Note that these thresholds are different between the STEP400 and
    STEP800.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+

    **STEP400:**

    +---------+---------------+----------------+-----------------+
    |TH_STATUS|Description    |Enable Threshold|Disable Threshold|
    +---------+---------------+----------------+-----------------+
    |0        |Normal         |-               |-                |
    +---------+---------------+----------------+-----------------+
    |1        |Warning        |135°C           |125°C            |
    +---------+---------------+----------------+-----------------+
    |2        |Bridge shutdown|155°C           |145°C            |
    +---------+---------------+----------------+-----------------+
    |3        |Device shutdown|170°C           |130°C            |
    +---------+---------------+----------------+-----------------+

    **STEP800:**

    +---------+---------------+----------------+-----------------+
    |TH_STATUS|Description    |Enable Threshold|Disable Threshold|
    +---------+---------------+----------------+-----------------+
    |0        |Normal         |-               |-                |
    +---------+---------------+----------------+-----------------+
    |1        |Warning        |130°C           |130°C            |
    +---------+---------------+----------------+-----------------+
    |2        |Bridge shutdown|160°C           |130°C            |
    +---------+---------------+----------------+-----------------+
    """

    address: str = field(default="/getThermalStatus", init=False)
    response_cls: responses.ThermalStatus = field(
        default=responses.ThermalStatus, init=False
    )
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """


@dataclass
class EnableOverCurrentReport(OSCSetCommand):
    """Enable or disable the automatic reporting of overcurrent events.

    Overcurrent events are sent whenever the motor driver exceeds the
    configured threshold. This threshold can be set using
    :py:class:`stepseries.commands.SetOverCurrentThreshold`.

    When overcurrent draw is detected, the device automatically enters a
    HiZ state with or without notification.

    This report is enabled by default.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/enableOverCurrentReport", init=False)
    response_cls: responses.OverCurrent = field(
        default=responses.OverCurrent, init=False
    )
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """
    enable: bool
    """If True, enable the reporting.

    +-------+----+
    |Default|True|
    +-------+----+
    """
    callback: Optional[Callable[..., None]] = None


@dataclass
class SetOverCurrentThreshold(OSCSetCommand):
    """Sets the overcurrent detection threshold.

    Note that these thresholds are different between the STEP400 and
    STEP800.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/setOverCurrentThreshold", init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """
    OCD_TH: int
    """The overcurrent threshold.

    **STEP400:**

    +-------+---------+
    |OCD_TH |Threshold|
    +-------+---------+
    |0      |312.5 mA |
    +-------+---------+
    |1      |625 mA   |
    +-------+---------+
    |...    |...      |
    +-------+---------+
    |30     |9.6875 A |
    +-------+---------+
    |31     |10 A     |
    +-------+---------+
    |Default|15 (5A)  |
    +-------+---------+

    **STEP800:**

    +-------+---------+
    |OCD_TH |Threshold|
    +-------+---------+
    |0      |375 mA   |
    +-------+---------+
    |1      |750 mA   |
    +-------+---------+
    |...    |...      |
    +-------+---------+
    |30     |5.625 A  |
    +-------+---------+
    |31     |6 A      |
    +-------+---------+
    |Default|7 (3A)   |
    +-------+---------+
    """


@dataclass
class GetOverCurrentThreshold(OSCGetCommand):
    """Retrieve the overcurrent threshold for a motor.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/getOverCurrentThreshold", init=False)
    response_cls: responses.OverCurrentThreshold = field(
        default=responses.OverCurrentThreshold, init=False
    )
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """


@dataclass
class EnableStallReport(OSCSetCommand):
    """Enable or disable the automatic reporting of stall events.

    The threshold can be set with
    :py:class:`stepseries.commands.SetStallThreshold`.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/enableStallReport", init=False)
    response_cls: responses.Stall = field(default=responses.Stall, init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """
    enable: bool
    """If True, enable the reporting.

    +-------+-----+
    |Default|False|
    +-------+-----+
    """
    callback: Optional[Callable[..., None]] = None


@dataclass
class SetStallThreshold(OSCSetCommand):
    """Sets the stall detection threshold.

    Note that these thresholds are different between the STEP400 and
    STEP800.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/setStallThreshold", init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """
    STALL_TH: int
    """The stall threshold.

    **STEP400:**

    +---------+---------+
    |STALL_TH |Threshold|
    +---------+---------+
    |0        |312.5 mA |
    +---------+---------+
    |1        |625 mA   |
    +---------+---------+
    |...      |...      |
    +---------+---------+
    |30       |9.6875 A |
    +---------+---------+
    |31       |10 A     |
    +---------+---------+
    |Default  |31 (10A) |
    +---------+---------+

    **STEP800:**

    +---------+---------+
    |STALL_TH |Threshold|
    +---------+---------+
    |0        |31.25 mA |
    +---------+---------+
    |1        |62.5 mA  |
    +---------+---------+
    |...      |...      |
    +---------+---------+
    |126      |3.969 A  |
    +---------+---------+
    |127      |4 A      |
    +---------+---------+
    |Default  |127 (4A) |
    +---------+---------+
    """


@dataclass
class GetStallThreshold(OSCGetCommand):
    """Retrieve the stall threshold for a motor.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/getStallThreshold", init=False)
    response_cls: responses.StallThreshold = field(
        default=responses.StallThreshold, init=False
    )
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """


@dataclass
class SetProhibitMotionOnHomeSw(OSCSetCommand):
    """
    Prohibit motion towards the homing direction when the home sensor is
    activated.

    The direction to the origin point can be configured using the
    `Config Tool`_ or with
    :py:class:`stepseries.commands.SetHomingDirection`.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+

    .. _Config Tool: http://ponoor.com/tools/step400-config/
    """

    address: str = field(default="/setProhibitMotionOnHomeSw", init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """
    enable: bool
    """If True, disable motion in the origin direction.

    +-------+-----+
    |Default|False|
    +-------+-----+
    """


@dataclass
class GetProhibitMotionOnHomeSw(OSCGetCommand):
    """
    Retrieve if motion towards the homing direction is disabled when the
    home switch is activated.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/getProhibitMotionOnHomeSw", init=False)
    response_cls: responses.ProhibitMotionOnHomeSw = field(
        default=responses.ProhibitMotionOnHomeSw, init=False
    )
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """


@dataclass
class SetProhibitMotionOnLimitSw(OSCSetCommand):
    """
    Prohibit motion in the opposite direction of the homing direction
    when the limit sensor is activated.

    The direction to the origin point can be configured using the
    `Config Tool`_ or with
    :py:class:`stepseries.commands.SetHomingDirection`.

    ``STEP400 Only``

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+

    .. _Config Tool: http://ponoor.com/tools/step400-config/
    """

    address: str = field(default="/setProhibitMotionOnLimitSw", init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    """
    enable: bool
    """If True, disable motion in the LIMIT switch direction.

    +-------+-----+
    |Default|False|
    +-------+-----+
    """


@dataclass
class GetProhibitMotionOnLimitSw(OSCGetCommand):
    """
    Retrieve if motion in the opposite of the homing direction is
    disabled when the limit switch is activated.

    ``STEP400 Only``

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/getProhibitMotionOnLimitSw", init=False)
    response_cls: responses.ProhibitMotionOnLimitSw = field(
        default=responses.ProhibitMotionOnLimitSw, init=False
    )
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    """


# Voltage and Current Mode Settings


@dataclass
class SetVoltageMode(OSCSetCommand):
    """Switch a specific motor into voltage mode.

    ``STEP400 Only``

    .. note:: The STEP800 is always in voltage mode and cannot be
        switched.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/setVoltageMode", init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    """


@dataclass
class SetKval(OSCSetCommand):
    """Sets the configuration for all four KVAL parameters.

    KVAL only applies when the motor controller is in voltage mode. This
    goes without saying KVAL always applies on the STEP800.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/setKval", init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """
    holdKVAL: int
    """KVAL for holding the motor's position.

    +-----------+-----+
    |Valid Range|0-255|
    +-----------+-----+
    |Default    |16   |
    +-----------+-----+
    """
    runKVAL: int
    """KVAL for maintaining the motor's speed.

    +-----------+-----+
    |Valid Range|0-255|
    +-----------+-----+
    |Default    |16   |
    +-----------+-----+
    """
    accKVAL: int
    """KVAL for accelerating the motor's speed.

    +-----------+-----+
    |Valid Range|0-255|
    +-----------+-----+
    |Default    |16   |
    +-----------+-----+
    """
    decKVAL: int
    """KVAL for decelerating the motor's speed.

    +-----------+-----+
    |Valid Range|0-255|
    +-----------+-----+
    |Default    |16   |
    +-----------+-----+
    """


@dataclass
class GetKval(OSCGetCommand):
    """Retrieves the four KVAL parameters for a specified motor.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/getKval", init=False)
    response_cls: responses.Kval = field(default=responses.Kval, init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """


@dataclass
class SetBemfParam(OSCSetCommand):
    """Sets the BEMF compensation register.

    BEMF only applies when the motor controller is in voltage mode. This
    goes without saying BEMF always applies on the STEP800.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/setBemfParam", init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """
    INT_SPEED: int
    """INT_SPEED register.

    +-----------+-------+
    |Valid Range|0-16383|
    +-----------+-------+
    |Default    |1032   |
    +-----------+-------+
    """
    ST_SLP: int
    """ST_SLP register.

    +-----------+-------+
    |Valid Range|0-255  |
    +-----------+-------+
    |Default    |25     |
    +-----------+-------+
    """
    FN_SLP_ACC: int
    """FN_SLP_ACC register.

    +-----------+-------+
    |Valid Range|0-255  |
    +-----------+-------+
    |Default    |41     |
    +-----------+-------+
    """
    FN_SLP_DEC: int
    """FN_SLP_DEC register.

    +-----------+-------+
    |Valid Range|0-255  |
    +-----------+-------+
    |Default    |41     |
    +-----------+-------+
    """


@dataclass
class GetBemfParam(OSCGetCommand):
    """Retrieves the BEMF compensation register.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/getBemfParam", init=False)
    response_cls: responses.BemfParam = field(default=responses.BemfParam, init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """


@dataclass
class SetCurrentMode(OSCSetCommand):
    """Switch a specific motor into current mode.

    ``STEP400 Only``

    .. note:: The STEP800 is always in voltage mode and cannot be
        switched.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/setCurrentMode", init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    """


@dataclass
class SetTval(OSCSetCommand):
    """Sets the configuration for all four TVAL parameters.

    ``STEP400 Only``

    TVAL only applies when the motor controller is in current mode. This
    goes without saying TVAL never applies on the STEP800.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/setTval", init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    """
    holdTVAL: int
    """TVAL for holding the motor's position.

    +-----------+-----+
    |Valid Range|0-127|
    +-----------+-----+
    |Default    |16   |
    +-----------+-----+
    """
    runTVAL: int
    """TVAL for maintaining the motor's speed.

    +-----------+-----+
    |Valid Range|0-127|
    +-----------+-----+
    |Default    |16   |
    +-----------+-----+
    """
    accTVAL: int
    """TVAL for accelerating the motor's speed.

    +-----------+-----+
    |Valid Range|0-127|
    +-----------+-----+
    |Default    |16   |
    +-----------+-----+
    """
    setDecTVAL: int
    """TVAL for decelerating the motor's speed.

    +-----------+-----+
    |Valid Range|0-127|
    +-----------+-----+
    |Default    |16   |
    +-----------+-----+
    """


@dataclass
class GetTval(OSCGetCommand):
    """Retrieves the configuration for all four TVAL parameters.

    ``STEP400 Only``

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/getTval", init=False)
    response_cls: responses.Tval = field(default=responses.Tval, init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    """


@dataclass
class GetTval_mA(OSCGetCommand):
    """Retrieves the configuration for all four TVAL parameters.

    Unlike :py:class:`stepseries.commands.GetTval`, this returns the
    actual current values (in mA), not the register values.

    ``STEP400 Only``

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/getTval_mA", init=False)
    response_cls: responses.Tval_mA = field(default=responses.Tval_mA, init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    """


@dataclass
class SetDecayModeParam(OSCSetCommand):
    """Sets the current control algorithm parameters.

    ``STEP400 Only``

    Decay mode only applies when the motor controller is in current
    mode. This goes without saying decay mode never applies on the
    STEP800.

    +-----------------+---+
    |Executable Timing|HiZ|
    +-----------------+---+
    """

    address: str = field(default="/setDecayModeParam", init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    """
    T_FAST: int
    """T_FAST register value.

    +-----------+-----+
    |Valid Range|0-255|
    +-----------+-----+
    |Default    |25   |
    +-----------+-----+
    """
    TON_MIN: int
    """TON_MIN register value.

    +-----------+-----+
    |Valid Range|0-255|
    +-----------+-----+
    |Default    |41   |
    +-----------+-----+
    """
    TOFF_MIN: int
    """TOFF_MIN register value.

    +-----------+-----+
    |Valid Range|0-255|
    +-----------+-----+
    |Default    |41   |
    +-----------+-----+
    """


@dataclass
class GetDecayModeParam(OSCGetCommand):
    """Retrieves the current control algorithm parameters.

    ``STEP400 Only``

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/getDecayModeParam", init=False)
    response_cls: responses.DecayModeParam = field(
        default=responses.DecayModeParam, init=False
    )
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    """


# Speed Profile


@dataclass
class SetSpeedProfile(OSCSetCommand):
    """Sets multiple speed profile settings at once.

    Acceleration, deceleration and max speed can all be set at once
    using this command.

    +-----------------+-------+
    |Executable Timing|Stopped|
    +-----------------+-------+
    """

    address: str = field(default="/setSpeedProfile", init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """
    acc: float
    """Acceleration.

    +-----------+-------------------------+
    |Valid Range|14.55 - 59590 [steps/s/s]|
    +-----------+-------------------------+
    |Default    |2000 [steps/s/s]         |
    +-----------+-------------------------+
    """
    dec: float
    """Deceleration.

    +-----------+-------------------------+
    |Valid Range|14.55 - 59590 [steps/s/s]|
    +-----------+-------------------------+
    |Default    |2000 [steps/s/s]         |
    +-----------+-------------------------+
    """
    maxSpeed: float
    """Maximum speed.

    +-----------+-----------------------+
    |Valid Range|15.25 - 15610 [steps/s]|
    +-----------+-----------------------+
    |Default    |620 [steps/s]          |
    +-----------+-----------------------+
    """


@dataclass
class GetSpeedProfile(OSCGetCommand):
    """Retrieves all three speed profile settings.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/getSpeedProfile", init=False)
    response_cls: responses.SpeedProfile = field(
        default=responses.SpeedProfile, init=False
    )
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """


@dataclass
class SetFullstepSpeed(OSCSetCommand):
    """Sets the threshold when microstepping switches to full stepping.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/setFullstepSpeed", init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """
    fullstepSpeed: float
    """Full-step speed.

    +-----------+----------------------+
    |Valid Range|7.63 - 15625 [steps/s]|
    +-----------+----------------------+
    |Default    |15625 [steps/s]       |
    +-----------+----------------------+
    """


@dataclass
class GetFullstepSpeed(OSCGetCommand):
    """Retrieves the switch threshold of microstepping to fullstepping.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/getFullstepSpeed", init=False)
    response_cls: responses.FullstepSpeed = field(
        default=responses.FullstepSpeed, init=False
    )
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """


@dataclass
class SetMaxSpeed(OSCSetCommand):
    """Set the maximum speed of the speed profile.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/setMaxSpeed", init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """
    maxSpeed: float
    """Maximum speed.

    +-----------+-----------------------+
    |Valid Range|15.25 - 15610 [steps/s]|
    +-----------+-----------------------+
    |Default    |620 [steps/s]          |
    +-----------+-----------------------+
    """


@dataclass
class SetAcc(OSCSetCommand):
    """Sets the acceleration of the speed profile.

    +-----------------+-------+
    |Executable Timing|Stopped|
    +-----------------+-------+
    """

    address: str = field(default="/setAcc", init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """
    acc: float
    """Acceleration.

    +-----------+-------------------------+
    |Valid Range|14.55 - 59590 [steps/s/s]|
    +-----------+-------------------------+
    |Default    |2000 [steps/s/s]         |
    +-----------+-------------------------+
    """


@dataclass
class SetDec(OSCSetCommand):
    """Sets the deceleration of the speed profile.

    +-----------------+-------+
    |Executable Timing|Stopped|
    +-----------------+-------+
    """

    address: str = field(default="/setDec", init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """
    dec: float
    """Deceleration.

    +-----------+-------------------------+
    |Valid Range|14.55 - 59590 [steps/s/s]|
    +-----------+-------------------------+
    |Default    |2000 [steps/s/s]         |
    +-----------+-------------------------+
    """


@dataclass
class SetMinSpeed(OSCSetCommand):
    """Sets the minimum speed of the speed profile.

    Also used for the motor speed of
    :py:class:`stepseries.commands.ReleaseSw`.

    If :py:class:`stepseries.commands.EnableLowSpeedOptimize` is
    enabled, the this is automatically set to zero.

    +-----------------+-------+
    |Executable Timing|Stopped|
    +-----------------+-------+
    """

    address: str = field(default="/setMinSpeed", init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """
    minSpeed: float
    """Minimum speed.

    +-----------+-------------------+
    |Valid Range|0 - 976.3 [steps/s]|
    +-----------+-------------------+
    |Default    |0 [steps/s]        |
    +-----------+-------------------+
    """


@dataclass
class GetMinSpeed(OSCGetCommand):
    """Retrieve the minimum speed of the speed profile.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/getMinSpeed", init=False)
    response_cls: responses.MinSpeed = field(default=responses.MinSpeed, init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """


@dataclass
class GetSpeed(OSCGetCommand):
    """Retrieve the current motor speed.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/getSpeed", init=False)
    response_cls: responses.Speed = field(default=responses.Speed, init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """


# Homing


@dataclass
class Homing(OSCSetCommand):
    """Start homing the motor.

    The motor will start moving towards the origin point and then stop
    when the HOME switch activates. The motor will then slowly reverse
    until the HOME switch releases. The home point will be set to this
    point.

    This command is essentially the combined functionality of
    :py:class:`stepseries.commands.GoUntil` and
    :py:class:`stepseries.commands.ReleaseSw`.

    Homing direction and speed can be set with
    :py:class:`stepseries.commands.SetHomingDirection` and
    :py:class:`stepseries.commands.SetHomingSpeed`, respectively; or
    configured with the `Config Tool`_.

    If the motor does not reach the HOME switch before
    :py:class:`stepseries.commands.SetGoUntilTimeout` or release the
    HOME switch before
    :py:class:`stepseries.commands.SetReleaseSwTimeout`, then the
    controller will halt the motor's movements.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+

    .. _Config Tool: http://ponoor.com/tools/step400-config/
    """

    address: str = field(default="/homing", init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """


@dataclass
class GetHomingStatus(OSCGetCommand):
    """Retrieve the homing status of a motor.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/getHomingStatus", init=False)
    response_cls: responses.HomingStatus = field(
        default=responses.HomingStatus, init=False
    )
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """


@dataclass
class SetHomingDirection(OSCSetCommand):
    """Sets the homing direction for homing.

    Can also be configured with the `Config Tool`_.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+

    .. _Config Tool: http://ponoor.com/tools/step400-config/
    """

    address: str = field(default="/setHomingDirection", init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """
    direction: bool
    """True or False, depending on your environment.

    +-------+-----+
    |Default|False|
    +-------+-----+
    """


@dataclass
class GetHomingDirection(OSCGetCommand):
    """Retrieve the homing direction for a motor.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/getHomingDirection", init=False)
    response_cls: responses.HomingDirection = field(
        default=responses.HomingDirection, init=False
    )
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """


@dataclass
class SetHomingSpeed(OSCSetCommand):
    """Set the homing speed for a motor.

    Can also be configured with the `Config Tool`_.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+

    .. _Config Tool: http://ponoor.com/tools/step400-config/
    """

    address: str = field(default="/setHomingSpeed", init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """
    speed: float
    """Speed to run at.

    +-----------+-----------------------+
    |Valid Range|0.0 - 15625.0 [steps/s]|
    +-----------+-----------------------+
    |Default    |100.0 [steps/s]        |
    +-----------+-----------------------+
    """


@dataclass
class GetHomingSpeed(OSCGetCommand):
    """Retrieve the homing speed for a motor.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/getHomingSpeed", init=False)
    response_cls: responses.HomingSpeed = field(
        default=responses.HomingSpeed, init=False
    )
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """


@dataclass
class GoUntil(OSCSetCommand):
    """Run a motor until the HOME switch activates or times out.

    The motor will run at the speed and direction according to the
    ``speed`` parameter.

    By default, the motor will soft stop unless if
    :py:class:`stepseries.commands.SetSwMode` is set to 0.

    The timeout for this command can be set using
    :py:class:`stepseries.commands.SetGoUntilTimeout`.

    This command is not influenced by
    :py:class:`stepseries.commands.SetHomingSpeed` or
    :py:class:`stepseries.commands.SetHomingDirection`.

    The motor is kept in a BUSY state until this command finishes.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/goUntil", init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """
    ACT: bool
    """The action to take when the HOME switch activates.

    +-------+----------------------------------------------+
    |0      |Set the origin (home) position here           |
    +-------+----------------------------------------------+
    |1      |Copy the current position to the MARK register|
    +-------+----------------------------------------------+
    """
    speed: float
    """The direction and speed to run.

    Direction can be set by specifying a positive or negative value.

    +-----------+----------------------------+
    |Valid Range|-15625.0 - 15625.0 [steps/s]|
    +-----------+----------------------------+
    |Default    |100 [steps/s]               |
    +-----------+----------------------------+
    """


@dataclass
class SetGoUntilTimeout(OSCSetCommand):
    """Set the timeout for :py:class:`stepseries.commands.GoUntil`.

    If the HOME switch is not activated before this timeout, then the
    controller stops the motor's movements. Specify 0 to disable the
    timeout.

    Can also be configured with the `Config Tool`_.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+

    .. _Config Tool: http://ponoor.com/tools/step400-config/
    """

    address: str = field(default="/setGoUntilTimeout", init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """
    timeOut: int
    """How long to wait for the HOME switch to activate.

    +-----------+-------------------+
    |Valid Range|0 - 4294967295 [ms]|
    +-----------+-------------------+
    |Default    |10000 [ms]         |
    +-----------+-------------------+
    """


@dataclass
class GetGoUntilTimeout(OSCGetCommand):
    """Retrieve the timeout for :py:class:`stepseries.commands.GoUntil`.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/getGoUntilTimeout", init=False)
    response_cls: responses.GoUntilTimeout = field(
        default=responses.GoUntilTimeout, init=False
    )
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """


@dataclass
class ReleaseSw(OSCSetCommand):
    """Move at a minimum speed until the HOME switch releases.

    On release, the controller will hard stop the motor and then process
    the motor's position according to ``ACT``.

    The timeout for this command can be set using
    :py:class:`stepseries.commands.SetReleaseSwTimeout`.

    This command is not influenced by
    :py:class:`stepseries.commands.SetHomingSpeed` or
    :py:class:`stepseries.commands.SetHomingDirection`.

    The motor is kept in a BUSY state until this command finishes.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/releaseSw", init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """
    ACT: bool
    """The action to take when the HOME switch releases.

    +-------+----------------------------------------------+
    |0      |Set the origin (home) position here           |
    +-------+----------------------------------------------+
    |1      |Copy the current position to the MARK register|
    +-------+----------------------------------------------+
    """
    DIR: bool
    """True or False, depending on your environment."""


@dataclass
class SetReleaseSwTimeout(OSCSetCommand):
    """Set the timeout for :py:class:`stepseries.commands.ReleaseSw`.

    If the HOME switch is not releaseed before this timeout, then the
    controller stops the motor's movements. Specify 0 to disable the
    timeout.

    Can also be configured with the `Config Tool`_.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+

    .. _Config Tool: http://ponoor.com/tools/step400-config/
    """

    address: str = field(default="/setReleaseSwTimeout", init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """
    timeOut: int
    """How long to wait for the HOME switch to activate.

    +-----------+-------------------+
    |Valid Range|0 - 4294967295 [ms]|
    +-----------+-------------------+
    |Default    |10000 [ms]         |
    +-----------+-------------------+
    """


@dataclass
class GetReleaseSwTimeout(OSCGetCommand):
    """
    Retrieve the timeout for :py:class:`stepseries.commands.ReleaseSw`.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/getReleaseSwTimeout", init=False)
    response_cls: responses.ReleaseSwTimeout = field(
        default=responses.ReleaseSwTimeout, init=False
    )
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """


# Home and Limit Sensors


@dataclass
class EnableHomeSwReport(OSCSetCommand):
    """Enable or disable the automatic reporting of home switch changes.

    Also see :py:class:`stepseries.commands.EnableSwEventReport`.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/enableHomeSwReport", init=False)
    response_cls: responses.HomeSw = field(default=responses.HomeSw, init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """
    enable: bool
    """If True, enable the reporting.

    +-------+-----+
    |Default|False|
    +-------+-----+
    """
    callback: Optional[Callable[..., None]] = None


@dataclass
class EnableSwEventReport(OSCSetCommand):
    """Enable or disable the automatic reporting of home switch changes.

    While very similar to
    :py:class:`stepseries.commands.EnableHomeSwReport` which polls the
    motor driver for the status of the home switch, this report
    essentially "listens" for a notification from the motor driver chip.
    This report is able to detect the closure of the home switch in
    under 1ms.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/enableSwEventReport", init=False)
    response_cls: responses.SwEvent = field(default=responses.SwEvent, init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """
    enable: bool
    """If True, enable the reporting.

    +-------+-----+
    |Default|False|
    +-------+-----+
    """
    callback: Optional[Callable[..., None]] = None


@dataclass
class GetHomeSw(OSCGetCommand):
    """Retrieve the status of the home switch.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/getHomeSw", init=False)
    response_cls: responses.HomeSw = field(default=responses.HomeSw, init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """


@dataclass
class EnableLimitSwReport(OSCSetCommand):
    """Enable or disable automatic reporting of limit switch changes.

    ``STEP400 Only``

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/enableLimitSwReport", init=False)
    response_cls: responses.LimitSw = field(default=responses.LimitSw, init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    """
    enable: bool
    """If True, enable the reporting.

    +-------+-----+
    |Default|False|
    +-------+-----+
    """
    callback: Optional[Callable[..., None]] = None


@dataclass
class GetLimitSw(OSCGetCommand):
    """Retrieve the status of the limit switch.

    ``STEP400 Only``

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/getLimitSw", init=False)
    response_cls: responses.LimitSw = field(default=responses.LimitSw, init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    """


@dataclass
class SetHomeSwMode(OSCSetCommand):
    """Configure whether to stop immediately on home switch release.

    +-----------------+---+
    |Executable Timing|HiZ|
    +-----------------+---+
    """

    address: str = field(default="/setHomeSwMode", init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """
    SW_MODE: bool
    """If True, do not stop.

    +-------+-------------------+
    |False  |Hard stop the motor|
    +-------+-------------------+
    |True   |Do not stop        |
    +-------+-------------------+
    |Default|True               |
    +-------+-------------------+
    """


@dataclass
class GetHomeSwMode(OSCGetCommand):
    """Retrieve the configured mode for the home switch.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/getHomeSwMode", init=False)
    response_cls: responses.HomeSwMode = field(default=responses.HomeSwMode, init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """


@dataclass
class SetLimitSwMode(OSCSetCommand):
    """Configure whether to stop immediately on limit switch activated.

    ``STEP400 Only``

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/setLimitSwMode", init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    """
    SW_MODE: bool
    """If True, do not stop.

    +-------+-------------------+
    |False  |Hard stop the motor|
    +-------+-------------------+
    |True   |Do not stop        |
    +-------+-------------------+
    |Default|True               |
    +-------+-------------------+
    """


@dataclass
class GetLimitSwMode(OSCGetCommand):
    """Retrieve the configured mode for the limit switch.

    ``STEP400 Only``

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/getLimitSwMode", init=False)
    response_cls: responses.LimitSwMode = field(
        default=responses.LimitSwMode, init=False
    )
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    """


# Position Management


@dataclass
class SetPosition(OSCSetCommand):
    """Overwrites the motor's current position.

    +-----------------+-------+
    |Executable Timing|Stopped|
    +-----------------+-------+
    """

    address: str = field(default="/setPosition", init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """
    newPosition: int
    """Position to override with.

    +-----------+------------------+
    |Valid Range|-2097152 - 2097151|
    +-----------+------------------+
    """


@dataclass
class GetPosition(OSCGetCommand):
    """Retrieve the current position of the motor.

    Alternatively,
    :py:class:`stepseries.commands.SetPositionReportInterval` can be
    configured to periodically send the current position.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/getPosition", init=False)
    response_cls: responses.Position = field(default=responses.Position, init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """


@dataclass
class GetPositionList(OSCGetCommand):
    """Retrieve the current positions for ALL motors.

    Alternatively,
    :py:class:`stepseries.commands.SetPositionListReportInterval` can
    be configured to periodically send the current position.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/getPositionList", init=False)
    response_cls: responses.PositionList = field(
        default=responses.PositionList, init=False
    )


@dataclass
class ResetPos(OSCSetCommand):
    """Resets the motor's position to 0.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/resetPos", init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """


@dataclass
class SetElPos(OSCSetCommand):
    """Set the electrical position of the motor.

    Microstepping is expressed as step/128 and the value must match the
    current microstep mode.

    +-----------------+-------+
    |Executable Timing|Stopped|
    +-----------------+-------+
    """

    address: str = field(default="/setElPos", init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """
    newFullstep: int
    """
    +-----------+-----+
    |Valid Range|0 - 3|
    +-----------+-----+
    """
    newMicrostep: int
    """
    +-----------+-------+
    |Valid Range|0 - 127|
    +-----------+-------+
    """


@dataclass
class GetElPos(OSCGetCommand):
    """Retrieve the current electrical position of the motor.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/getElPos", init=False)
    response_cls: responses.ElPos = field(default=responses.ElPos, init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """


@dataclass
class SetMark(OSCSetCommand):
    """Set the MARK register to an arbitrary position.

    This register allows you store one position. Each write overwrites
    the last position set to this register.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/setMark", init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """
    MARK: int
    """Point to be set."""


@dataclass
class GetMark(OSCGetCommand):
    """Retrieve the MARK position.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/getMark", init=False)
    response_cls: responses.Mark = field(default=responses.Mark, init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """


@dataclass
class GoHome(OSCSetCommand):
    """Send this motor to its origin (zero) point.

    +-----------------+--------+
    |Executable Timing|Not Busy|
    +-----------------+--------+
    """

    address: str = field(default="/goHome", init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """


@dataclass
class GoMark(OSCSetCommand):
    """Send this motor to its MARK positon.

    +-----------------+--------+
    |Executable Timing|Not Busy|
    +-----------------+--------+
    """

    address: str = field(default="/goMark", init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """


# Motor Control


@dataclass
class Run(OSCSetCommand):
    """Run the motor at a constant speed.

    The motor follows the configured speed profile set with
    :py:class:`stepseries.commands.SetSpeedProfile`.

    Keeps the motor in the 'BUSY' state until ``speed`` has been
    reached.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/run", init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """
    speed: float
    """Speed to run the motor at.

    Negative values run the motor in reverse. Limited by the maximum
    and minimum speed set in the speed profile.

    +-----------+----------------------------+
    |Valid Range|-15625.0 - 15625.0 [steps/s]|
    +-----------+----------------------------+
    """


@dataclass
class Move(OSCSetCommand):
    """Move the motor the specified number of steps.

    Keeps the motor in the 'BUSY' state until the specified steps has
    been reached.

    +-----------------+-------+
    |Executable Timing|Stopped|
    +-----------------+-------+
    """

    address: str = field(default="/move", init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """
    step: int


@dataclass
class GoTo(OSCSetCommand):
    """Moves to the specified position in the shortest route possible.

    -2097152 and 2097151 are next to each other in the driver chip, like
    how 0 and 360 are on a circle. This means if you specify 2097000 and
    the motor is currently at -2097000, then the motor will move to
    -2097152, then 2097151, and finally 2097000.

    Alternatively, :py:class:`stepseries.commands.GoToDir` can be used
    to specific the direction in addition to the position.

    Keeps the motor in the 'BUSY' state until the specified position has
    been reached.

    +-----------------+--------+
    |Executable Timing|Not Busy|
    +-----------------+--------+
    """

    address: str = field(default="/goTo", init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """
    position: int
    """
    +-----------+------------------+
    |Valid Range|-2097152 - 2097151|
    +-----------+------------------+
    """


@dataclass
class GoToDir(OSCSetCommand):
    """Moves to specified position in the specified direction.

    -2097152 and 2097151 are next to each other in the driver chip, like
    how 0 and 360 are on a circle. As an example, if you specify
    2097000, True (forward) and the motor is currently at -2097000, then
    the motor will move to -2000000, then 0, and finally 2097000.

    Alternatively, :py:class:`stepseries.commands.GoTo` will
    automatically determine the shortest route (around that 'circle').

    Keeps the motor in the 'BUSY' state until the specified position has
    been reached.

    +-----------------+--------+
    |Executable Timing|Not Busy|
    +-----------------+--------+
    """

    address: str = field(default="/goToDir", init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """
    DIR: bool
    """True for forward, False for backward."""
    position: int
    """
    +-----------+------------------+
    |Valid Range|-2097152 - 2097151|
    +-----------+------------------+
    """


@dataclass
class SoftStop(OSCSetCommand):
    """Stops the motor according to the speed profile.

    After decelerating and stopping, the motor is kept in an excited
    state if it was originally in a HiZ state. Remains in the BUSY state
    until the motor stops.

    If it was in servo mode, then the mode will be released.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/softStop", init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """


@dataclass
class HardStop(OSCSetCommand):
    """Immediately stops the motor.

    After stopping, the motor is kept in an excited state if it was
    originally in a HiZ state.

    If it was in servo mode, then the mode will be released.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/hardStop", init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """


@dataclass
class SoftHiZ(OSCSetCommand):
    """Stops the motor according to the speed profile.

    When stopped, the motor's excitation is released. If the
    electromagnetic brake is enabled, then the brake is put into a hold
    state before excitation is released. Transitions to HiZ after
    excitation is released. Remains in the BUSY state until the motor
    stops.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/softHiZ", init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """


@dataclass
class HardHiZ(OSCSetCommand):
    """Immediately stops the motor.

    When stopped, the motor's excitation is released. If the
    electromagnetic brake is enabled, then the brake is put into a hold
    state before excitation is released. Transitions to HiZ after
    excitation is released. Remains in the BUSY state until the motor
    stops.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/hardHiZ", init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """


# Electromagnetic Brake


@dataclass
class EnableElectromagnetBrake(OSCSetCommand):
    """Enable or disable electromagnetic brake operation.

    Not to be confused with :py:class:`stepseries.commands.Activate`
    which activates or deactivates the brake.

    While enabled, the controller will reply with
    ``ERROR_BRAKE_ENGAGED`` if a movement command is sent without
    releasing the brake.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/enableElectromagnetBrake", init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """
    enable: bool
    """If True, enable the brake.

    +-------+-----+
    |Default|False|
    +-------+-----+
    """


@dataclass
class Activate(OSCSetCommand):
    """Enables or disables the electromagnetic brake.

    :py:class:`stepseries.commands.EnableElectromagnetBrake` must be
    enabled for this command to have an effect.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/activate", init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """
    state: bool
    """
    +-+-----------------------------+
    |0|Motor engaged, brake released|
    +-+-----------------------------+
    |1|Motor released, brake engaged|
    +-+-----------------------------+
    """


@dataclass
class Free(OSCSetCommand):
    """Releases both the motor and brake.

    .. warning:: If **any** load is attached to the motor, it will no
        longer be held when this command is sent.

    :py:class:`stepseries.commands.EnableElectromagnetBrake` must be
    enabled for this command to have an effect.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/free", init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """


@dataclass
class SetBrakeTransitionDuration(OSCSetCommand):
    """Duration to keep the motor activated while the brake transitions.

    Due to the physical transition time of the brake, the motor needs to
    be engaged to cover this period.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/setBrakeTransitionDuration", init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """
    duration: int
    """
    +-----------+-------------+
    |Valid Range|0-10000  [ms]|
    +-----------+-------------+
    |Default    |100 [ms]     |
    +-----------+-------------+
    """


@dataclass
class GetBrakeTransitionDuration(OSCGetCommand):
    """Retrieve the brake transition duration.

    Due to the physical transition time of the brake, the motor needs to
    be engaged to cover this period which this command retrieves.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/getBrakeTransitionDuration", init=False)
    response_cls: responses.BrakeTransitionDuration = field(
        default=responses.BrakeTransitionDuration, init=False
    )
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """


# Servo Mode


@dataclass
class EnableServoMode(OSCSetCommand):
    """Enable or disable servo mode (position tracking mode).

    It is not possible to send other control commands such as
    :py:class:`stepseries.commands.Run` or
    :py:class:`stepseries.commands.GoTo` when in this mode.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/enableServoMode", init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """
    enable: bool
    """If True, enable servo mode.

    +-------+-----+
    |Default|False|
    +-------+-----+
    """


@dataclass
class SetServoParam(OSCSetCommand):
    """Configure the servo PID control parameters.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/setServoParam", init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """
    kP: float
    """Proportional gain.

    +-----------+----+
    |Valid Range|0-  |
    +-----------+----+
    |Default    |0.06|
    +-----------+----+
    """
    kI: float
    """Integral gain.

    +-----------+---+
    |Valid Range|0- |
    +-----------+---+
    |Default    |0.0|
    +-----------+---+
    """
    kD: float
    """Derivative gain.

    +-----------+---+
    |Valid Range|0- |
    +-----------+---+
    |Default    |0.0|
    +-----------+---+
    """


@dataclass
class GetServoParam(OSCGetCommand):
    """Retrieve the servo PID control parameters.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/getServoParam", init=False)
    response_cls: responses.ServoParam = field(default=responses.ServoParam, init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """


@dataclass
class SetTargetPosition(OSCSetCommand):
    """Set the target position to go to when in servo mode.

    :py:class:`stepseries.commands.EnableServoMode` must be enabled for
    this command to have an effect.

    +-----------------+------+
    |Executable Timing|Always|
    +-----------------+------+
    """

    address: str = field(default="/setTargetPosition", init=False)
    motorID: int
    """
    +-------+--------+
    |STEP400|1-4, 255|
    +-------+--------+
    |STEP800|1-8, 255|
    +-------+--------+
    """
    position: int
    """
    +-----------+------------------+
    |Valid Range|-2097152 - 2097151|
    +-----------+------------------+
    """


@dataclass
class SetTargetPositionList(OSCSetCommand):
    """Set the target positions of all motors at once.

    .. note:: If using the STEP400, positions 5-8 do not need to be
        configured.
    """

    address: str = field(default="/setTargetPositionList", init=False)
    position1: int
    """
    +-----------+------------------+
    |Valid Range|-2097152 - 2097151|
    +-----------+------------------+
    """
    position2: int
    """
    +-----------+------------------+
    |Valid Range|-2097152 - 2097151|
    +-----------+------------------+
    """
    position3: int
    """
    +-----------+------------------+
    |Valid Range|-2097152 - 2097151|
    +-----------+------------------+
    """
    position4: int
    """
    +-----------+------------------+
    |Valid Range|-2097152 - 2097151|
    +-----------+------------------+
    """
    position5: int = None
    """
    ``STEP800 only``

    +-----------+------------------+
    |Valid Range|-2097152 - 2097151|
    +-----------+------------------+
    """
    position6: int = None
    """
    ``STEP800 only``

    +-----------+------------------+
    |Valid Range|-2097152 - 2097151|
    +-----------+------------------+
    """
    position7: int = None
    """
    ``STEP800 only``

    +-----------+------------------+
    |Valid Range|-2097152 - 2097151|
    +-----------+------------------+
    """
    position8: int = None
    """
    ``STEP800 only``

    +-----------+------------------+
    |Valid Range|-2097152 - 2097151|
    +-----------+------------------+
    """
