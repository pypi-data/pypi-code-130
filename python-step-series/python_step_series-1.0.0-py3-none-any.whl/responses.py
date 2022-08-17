"""Messages received from the device."""


import ast
import re
from dataclasses import dataclass as _dataclass
from dataclasses import field
from typing import Any, Callable, Dict, Tuple, TypeVar, Union

# Pylance custom dataclass work around
_T = TypeVar("_T")


def __dataclass_transform__(
    *,
    eq_default: bool = True,
    order_default: bool = False,
    kw_only_default: bool = False,
    field_descriptors: Tuple[Union[type, Callable[..., Any]], ...] = (()),
) -> Callable[[_T], _T]:
    return lambda a: a


# Implement a custom dataclass to parse raw strings
@__dataclass_transform__(field_descriptors=(field,))
def dataclass(*args: Tuple[Any], **kwargs: Dict[str, Any]):
    def wrapper(cls):
        cls = _dataclass(cls, **kwargs)
        original_init = cls.__init__

        def __init__(self, *args, **kwargs):
            # Concat split string args
            if all([isinstance(x, str) for x in args]):
                args = (" ".join(args),)

            # Break down the args
            if len(args) == 1 and isinstance(args[0], str):
                # First look for custom regex strings
                # These will be <field_name>_re
                for i, field_name in enumerate(self.__annotations__.keys()):
                    if field_name.endswith("_re"):
                        match: re.Match = getattr(self, field_name).search(args[0])
                        kwargs[field_name[:-3]] = match[0]
                        args = (
                            (args[0][: match.start()] + args[0][match.end() :]).strip(),
                        )
                args = args[0].split()

                # Now add all to kwargs
                field_names = [
                    k
                    for k in self.__annotations__.keys()
                    if k not in kwargs and not k.endswith("_re")
                ]
                for i, arg in enumerate(args):
                    field_name = field_names[i]
                    kwargs[field_name] = arg
                args = tuple()
                kwargs.pop("address", None)

            # Remove unnecessary address identifier
            args = list(args)
            if args and args[0] == self.address:
                args.pop(0)

            # Eval positional args
            for i, arg in enumerate(args):
                try:
                    args[i] = ast.literal_eval(arg.capitalize())
                except (AttributeError, ValueError, SyntaxError, NameError):
                    # Catch errors for non-strings, bad strings (i.e. ture instead of true)
                    # or non-evalable strings (i.e. class name)
                    pass

            # Eval named args
            for k, v in kwargs.items():
                try:
                    kwargs[k] = ast.literal_eval(v.capitalize())
                except (AttributeError, ValueError, SyntaxError, NameError):
                    # Catch errors for non-strings, bad strings (i.e. ture instead of true)
                    # or non-evalable strings (i.e. class name)
                    pass

            # Now call the generated dataclass init
            original_init(self, *args, **kwargs)

        cls.__init__ = __init__
        return cls

    return wrapper(args[0]) if args else wrapper


@dataclass
class OSCResponse(object):
    """An abstract class meant to be implemented by OSC resp objects."""

    address: str


# Automatic Messages


@dataclass
class Booted(OSCResponse):
    """Sent when the device (re)starts.

    This message is sent regardless if
    :py:class:`stepseries.commands.SetDestIP` has been recieved. By
    watching for this message, you can determine when the device
    restarts even if unexpectedly.

    When the firmware has started and an ethernet uplink is confirmed,
    this message will be sent.

    This is a broadcast message meaning it is sent to all devices on the
    subnet (address ``255.255.255.255``). If this is unacceptable for
    your network, you can disable it via the `Config Tool`_.

    .. _Config Tool: http://ponoor.com/tools/step400-config/
    """

    address: str = field(default="/booted", init=False)
    deviceID: int
    """
    ===== ===================================
    Range Description
    ===== ===================================
    0-255 The device ID set by the DIP switch
    ===== ===================================
    """


@dataclass
class ErrorCommand(OSCResponse, Exception):
    """Sent if an error is detected while executing a command.

    Can be enabled or disabled with
    :py:class:`stepseries.commands.ReportError`.
    """

    address: str = field(default="/error/command", init=False)
    errorText: str
    """
    ================= ===========================================================================================================
    errorText	      Description
    ================= ===========================================================================================================
    CommandIgnored	  The command is currently not executable. Also refer to the ``Timing`` section.
    MotorIdNotMatch	  Motor ID is not appropriate.
    BrakeEngaging	  A motion command was sent while the electromagnetic brake was active.
    HomeSwActivating  A motion command to move in the homing direction was sent while the home sensor is active.
    LimitSwActivating A motion command to move in the opposite of the homing direction was sent while the limit sensor is active.
    GoUntilTimeout    Timed out while executing ``/goUntil`` command.
    ReleaseSwTimeout  Timed out while executing ``/releaseSw`` command.
    InServoMode       Received a command which can not be executed while servo mode.
    ================= ===========================================================================================================
    """
    motorID: int = None
    """
    ========== ===========
    Controller Motor Range
    ========== ===========
    STEP400    1-4
    STEP800    1-8
    ========== ===========
    """


@dataclass
class ErrorOSC(OSCResponse, Exception):
    """Sent if any error is detected in the OSC command."""

    address: str = field(default="/error/osc", init=False)
    errorText: str
    """
    =============== =================================
    errorText	    Description
    =============== =================================
    messageNotMatch	There is no corresponding command
    oscSyntaxError	The OSC format is out of standard
    WrongDataType	Wrong datatype of in argument(s)
    =============== =================================
    """
    motorID: int = None
    """
    ========== ===========
    Controller Motor Range
    ========== ===========
    STEP400    1-4
    STEP800    1-8
    ========== ===========
    """


@dataclass
class Busy(OSCResponse):
    """The BUSY state of a motor."""

    address: str = field(default="/busy", init=False)
    motorID: int
    """
    ========== ===========
    Controller Motor Range
    ========== ===========
    STEP400    1-4
    STEP800    1-8
    ========== ===========
    """
    state: int
    """
    ===== ====================
    Range Description
    ===== ====================
    0-1   1: BUSY, 0: Not BUSY
    ===== ====================
    """


@dataclass
class HiZ(OSCResponse):
    """The high-impedance (HiZ) state of a motor."""

    address: str = field(default="/HiZ", init=False)
    motorID: int
    """
    ========== ===========
    Controller Motor Range
    ========== ===========
    STEP400    1-4
    STEP800    1-8
    ========== ===========
    """
    state: int
    """
    ===== ==================
    Range Description
    ===== ==================
    0-1   1: HiZ, 0: Not HiZ
    ===== ==================
    """


@dataclass
class MotorStatus(OSCResponse):
    """The operating status of a motor."""

    address: str = field(default="/motorStatus", init=False)
    motorID: int
    """
    ========== ===========
    Controller Motor Range
    ========== ===========
    STEP400    1-4
    STEP800    1-8
    ========== ===========
    """
    MOT_STATUS: int
    """
    ===== ==============
    Range Description
    ===== ==============
    0     Stopped
    1     Acceleration
    2     Deceleration
    3     Constant Speed
    ===== ==============
    """


@dataclass
class HomingStatus(OSCResponse):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/automatically-sent-messages-from-step-400/#homingstatus"""  # noqa

    address: str = field(default="/homingStatus", init=False)
    motorID: int
    """
    ========== ===========
    Controller Motor Range
    ========== ===========
    STEP400    1-4
    STEP800    1-8
    ========== ===========
    """
    homingStatus: int


@dataclass
class Uvlo(OSCResponse):
    """The current state of undervoltage lockout of a motor."""

    address: str = field(default="/uvlo", init=False)
    motorID: int
    """
    ========== ===========
    Controller Motor Range
    ========== ===========
    STEP400    1-4
    STEP800    1-8
    ========== ===========
    """
    state: int
    """
    ===== ===================
    Range Description
    ===== ===================
    0-1   1: UVLO, 0: No UVLO
    ===== ===================
    """


@dataclass
class ThermalStatus(OSCResponse):
    """The thermal status of a motor driver chip.

    The thresholds between the STEP400 and STEP800 do vary.
    """

    address: str = field(default="/thermalStatus", init=False)
    motorID: int
    """
    ========== ===========
    Controller Motor Range
    ========== ===========
    STEP400    1-4
    STEP800    1-8
    ========== ===========
    """
    thermalStatus: int
    """
    **STEP400**:

    ===== =============== ============= =================
    Range Description     Set Threshold Release Threshold
    ===== =============== ============= =================
    0     Normal          N/A           N/A
    1     Warning         135°C         125°C
    2     Bridge Shutdown 155°C         145°C
    3     Device Shutdown 170°C         130°C
    ===== =============== ============= =================

    **STEP800**:

    ===== =============== ============= =================
    Range Description     Set Threshold Release Threshold
    ===== =============== ============= =================
    0     Normal          N/A           N/A
    1     Warning         130°C         130°C
    2     Bridge Shutdown 160°C         130°C
    ===== =============== ============= =================
    """


@dataclass
class OverCurrent(OSCResponse):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/automatically-sent-messages-from-step-400/#overcurrent"""  # noqa

    address: str = field(default="/overCurrent", init=False)
    motorID: int
    """
    ========== ===========
    Controller Motor Range
    ========== ===========
    STEP400    1-4
    STEP800    1-8
    ========== ===========
    """


@dataclass
class Stall(OSCResponse):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/automatically-sent-messages-from-step-400/#stall"""  # noqa

    address: str = field(default="/stall", init=False)
    motorID: int
    """
    ========== ===========
    Controller Motor Range
    ========== ===========
    STEP400    1-4
    STEP800    1-8
    ========== ===========
    """


# System Settings


@dataclass
class DestIP(OSCResponse):
    """Confirmation :py:class:`stepseries.commands.SetDestIP` has been
    recieved.
    """

    address: str = field(default="/destIp", init=False)
    destIp0: int
    """The first octet of the IP address set."""
    destIp1: int
    """The second octet of the IP address set."""
    destIp2: int
    """The third octet of the IP address set."""
    destIp3: int
    """The fourth octet of the IP address set."""
    isNewDestIp: int
    """Indicates if the IP address has changed from what is already set."""


@dataclass
class Version(OSCResponse):
    """The firmware version burnt onto the chip."""

    address: str = field(default="/version", init=False)
    firmware_name: str
    """Name of the firmware."""
    firmware_version: str
    """Version of the firmware."""
    compile_date: str
    """Compile date of the firmware"""

    # Custom regex to breakout
    compile_date_re: re.Pattern = field(
        default=re.compile(r"\w+ ? \d{1,2} \d{4} .+"),
        init=False,
        repr=False,
    )


@dataclass
class ConfigName(OSCResponse):
    """Metadata about the configuration file."""

    address: str = field(default="/configName", init=False)
    configName: str
    """Name of the configuration."""
    sdInitializeSucceeded: int
    """If the microSD card was successfully read."""
    configFileOpenSucceeded: int
    """If the device could open the configuration file."""
    configFileParseSucceeded: int
    """If the configuration was successfully parsed."""


# Motor Driver Settings


@dataclass
class MicrostepMode(OSCResponse):
    """The microstep mode of the motor."""

    address: str = field(default="/microstepMode", init=False)
    motorID: int
    """
    ========== ===========
    Controller Motor Range
    ========== ===========
    STEP400    1-4
    STEP800    1-8
    ========== ===========
    """
    STEP_SEL: int
    """
    ===== ===========
    Range Description
    ===== ===========
    0     Full-step
    1     Half-step
    2     1/4 step
    3     1/8 step
    4     1/16 step
    5     1/32 step
    6     1/64 step
    7     1/128 step
    ===== ===========
    """


@dataclass
class LowSpeedOptimizeThreshold(OSCResponse):
    """The threshold to enable low speed optimization."""

    address: str = field(default="/lowSpeedOptimizeThreshold", init=False)
    motorID: int
    """
    ========== ===========
    Controller Motor Range
    ========== ===========
    STEP400    1-4
    STEP800    1-8
    ========== ===========
    """
    lowSpeedOptimizeThreshold: float
    """0.0 - 976.3 steps/s"""
    optimizationEnabled: int
    """
    ===== =======================
    Range Description
    ===== =======================
    0-1   1: Enabled, 0: Disabled
    ===== =======================
    """


@dataclass
class Dir(OSCResponse):
    """The direction of a motor."""

    address: str = field(default="/dir", init=False)
    motorID: int
    """
    ========== ===========
    Controller Motor Range
    ========== ===========
    STEP400    1-4
    STEP800    1-8
    ========== ===========
    """
    direction: int
    """
    ===== ======================
    Range Description
    ===== ======================
    0-1   1: Forward, 0: Reverse
    ===== ======================
    """


@dataclass
class AdcVal(OSCResponse):
    """The ADC_OUT register value from the motor driver chip."""

    address: str = field(default="/adcVal", init=False)
    motorID: int
    """
    ========== ===========
    Controller Motor Range
    ========== ===========
    STEP400    1-4
    STEP800    1-8
    ========== ===========
    """
    ADC_OUT: int
    """
    ===== ======================================
    Range Description
    ===== ======================================
    0-31  5-bit read out of the ADC_OUT register
    ===== ======================================
    """


@dataclass
class Status(OSCResponse):
    """The STATUS of a motor.

    Refer to STATUS in the datasheet for the information contained in
    the registers. Some bits are latched and reset when the STATUS
    registers are read out. Because the firmware constantly reads these
    registers, they are immediately reset. It is possible to setup event
    to be reported depending on the data read, so please use those
    commands.

    ================ ======================== =========================================================
    STEP400 Bits     STEP800 Bits             Configuration Command
    ================ ======================== =========================================================
    UVLO             UVLO                     :py:class:`stepseries.commands.EnableUvloReport`
    UVLO_ADC         N/A                      Not implemented
    OCD              OCD                      :py:class:`stepseries.commands.EnableOverCurrentReport`
    STALL_A, STALL_B STEP_LOSS_A, STEP_LOSS_B :py:class:`stepseries.commands.EnableStallReport`
    CMD_ERROR        WRONG_CMD, NOTPREF_CMD   :py:class:`stepseries.commands.EnableCommandErrorReport`
    TH_STATUS        TH_WRN, TH_SD            :py:class:`stepseries.commands.EnableThermalStatusReport`
    SW_EVN           SW_EVN                   :py:class:`stepseries.commands.EnableHomeSwReport`
    MOT_STATUS       MOT_STATUS               :py:class:`stepseries.commands.EnableMotorStatusReport`
    SW_F             SW_F                     :py:class:`stepseries.commands.EnableHomeSwReport`
    BUSY             BUSY                     :py:class:`stepseries.commands.EnableBusyReport`
    HIZ              HIZ                      :py:class:`stepseries.commands.EnableHiZReport`
    ================ ======================== =========================================================
    """

    address: str = field(default="/status", init=False)
    motorID: int
    """
    ========== ===========
    Controller Motor Range
    ========== ===========
    STEP400    1-4
    STEP800    1-8
    ========== ===========
    """
    status: int
    """
    ======= =====================
    Range   Description
    ======= =====================
    0-65535 STATUS register value
    ======= =====================
    """


@dataclass
class ConfigRegister(OSCResponse):
    """The 16-bit CONFIG register value from the motor driver."""

    address: str = field(default="/configRegister", init=False)
    motorID: int
    """
    ========== ===========
    Controller Motor Range
    ========== ===========
    STEP400    1-4
    STEP800    1-8
    ========== ===========
    """
    CONFIG: int
    """0-65535 (0xFFFF)"""


# Alarm Settings


@dataclass
class OverCurrentThreshold(OSCResponse):
    """The threshold of over current in mA."""

    address: str = field(default="/overCurrentThreshold", init=False)
    motorID: int
    """
    ========== ===========
    Controller Motor Range
    ========== ===========
    STEP400    1-4
    STEP800    1-8
    ========== ===========
    """
    overCurrentThreshold: float
    """
    ========== =============
    Controller Range
    ========== =============
    STEP400    312.5-10000.0
    STEP800    375.0-6000.0
    ========== =============
    """


@dataclass
class StallThreshold(OSCResponse):
    """The stall detection threshold in mA."""

    address: str = field(default="/stallThreshold", init=False)
    motorID: int
    """
    ========== ===========
    Controller Motor Range
    ========== ===========
    STEP400    1-4
    STEP800    1-8
    ========== ===========
    """
    stallThreshold: float
    """
    ========== =============
    Controller Range
    ========== =============
    STEP400    312.5-10000.0
    STEP800    31.25-4000.0
    ========== =============
    """


@dataclass
class ProhibitMotionOnHomeSw(OSCResponse):
    """Whether motion towards the homing direction is permitted when HomeSw is active."""

    address: str = field(default="/prohibitMotionOnHomeSw", init=False)
    motorID: int
    """
    ========== ===========
    Controller Motor Range
    ========== ===========
    STEP400    1-4
    STEP800    1-8
    ========== ===========
    """
    enable: int
    """
    ===== =========================
    Range Description
    ===== =========================
    0-1   1: Prohibited, 0: Allowed
    ===== =========================
    """


@dataclass
class ProhibitMotionOnLimitSw(OSCResponse):
    """
    Whether motion to the opposite of the homing direction is permitted when LimitSw is active.
    """

    address: str = field(default="/prohibitMotionOnLimitSw", init=False)
    motorID: int
    """
    ========== ===========
    Controller Motor Range
    ========== ===========
    STEP400    1-4
    STEP800    1-8
    ========== ===========
    """
    enable: int
    """
    ===== =========================
    Range Description
    ===== =========================
    0-1   1: Prohibited, 0: Allowed
    ===== =========================
    """


# Voltage and Current Mode Settings


@dataclass
class Kval(OSCResponse):
    """All four KVALs together."""

    address: str = field(default="/kval", init=False)
    motorID: int
    """
    ========== ===========
    Controller Motor Range
    ========== ===========
    STEP400    1-4
    STEP800    1-8
    ========== ===========
    """
    holdKVAL: int
    """
    ===== =================
    Range Description
    ===== =================
    0-255 KVAL when stopped
    ===== =================
    """
    runKVAL: int
    """
    ===== =================
    Range Description
    ===== =================
    0-255 KVAL when stopped
    ===== =================
    """
    accKVAL: int
    """
    ===== =================
    Range Description
    ===== =================
    0-255 KVAL when stopped
    ===== =================
    """
    decKVAL: int
    """
    ===== =================
    Range Description
    ===== =================
    0-255 KVAL when stopped
    ===== =================
    """


@dataclass
class BemfParam(OSCResponse):
    """Register values for the BEMF parameter."""

    address: str = field(default="/bemfParam", init=False)
    motorID: int
    """
    ========== ===========
    Controller Motor Range
    ========== ===========
    STEP400    1-4
    STEP800    1-8
    ========== ===========
    """
    INT_SPEED: int
    """
    ================ ========================
    Range            Description
    ================ ========================
    0-16383 (0x3FFF) INT_SPEED register value
    ================ ========================
    """
    ST_SLP: int
    """
    ============ =====================
    Range        Description
    ============ =====================
    0-255 (0xFF) ST_SLP register value
    ============ =====================
    """
    FN_SLP_ACC: int
    """
    ============ =========================
    Range        Description
    ============ =========================
    0-255 (0xFF) FN_SLP_ACC register value
    ============ =========================
    """
    FN_SLP_DEC: int
    """
    ============ =========================
    Range        Description
    ============ =========================
    0-255 (0xFF) FN_SLP_DEC register value
    ============ =========================
    """


@dataclass
class Tval(OSCResponse):
    """All four TVALs together."""

    address: str = field(default="/tval", init=False)
    motorID: int
    """
    ========== ===========
    Controller Motor Range
    ========== ===========
    STEP400    1-4
    STEP800    1-8
    ========== ===========
    """
    holdTVAL: int
    """
    ===== =================
    Range Description
    ===== =================
    0-127 TVAL when stopped
    ===== =================
    """
    runTVAL: int
    """
    ===== ===========================
    Range Description
    ===== ===========================
    0-127 TVAL in constant speed mode
    ===== ===========================
    """
    accTVAL: int
    """
    ===== ========================
    Range Description
    ===== ========================
    0-127 TVAL during acceleration
    ===== ========================
    """
    decTVAL: int
    """
    ===== ========================
    Range Description
    ===== ========================
    0-127 TVAL during deceleration
    ===== ========================
    """


@dataclass
class Tval_mA(OSCResponse):
    """All four TVALs together but in mA, not register values."""

    address: str = field(default="/tval_mA", init=False)
    motorID: int
    """
    ========== ===========
    Controller Motor Range
    ========== ===========
    STEP400    1-4
    STEP800    1-8
    ========== ===========
    """
    holdTVAL_mA: float
    """
    =============== =================
    Range           Description
    =============== =================
    78.125 - 5000.0 TVAL when stopped
    =============== =================
    """
    runTVAL_mA: float
    """
    =============== ===========================
    Range           Description
    =============== ===========================
    78.125 - 5000.0 TVAL in constant speed mode
    =============== ===========================
    """
    accTVAL_mA: float
    """
    =============== ========================
    Range           Description
    =============== ========================
    78.125 - 5000.0 TVAL during acceleration
    =============== ========================
    """
    decTVAL_mA: float
    """
    =============== ========================
    Range           Description
    =============== ========================
    78.125 - 5000.0 TVAL during deceleration
    =============== ========================
    """


@dataclass
class DecayModeParam(OSCResponse):
    """Register values (parameters) for the current control algorithm."""

    address: str = field(default="/decayModeParam", init=False)
    motorID: int
    """
    ========== ===========
    Controller Motor Range
    ========== ===========
    STEP400    1-4
    STEP800    1-8
    ========== ===========
    """
    T_FAST: int
    """
    ============ =====================
    Range        Description
    ============ =====================
    0-255 (0xFF) T_FAST register value
    ============ =====================
    """
    TON_MIN: int
    """
    ============ ======================
    Range        Description
    ============ ======================
    0-255 (0xFF) TON_MIN register value
    ============ ======================
    """
    TOFF_MIN: int
    """
    ============ =======================
    Range        Description
    ============ =======================
    0-255 (0xFF) TOFF_MIN register value
    ============ =======================
    """


# Speed Profile


@dataclass
class SpeedProfile(OSCResponse):
    """The acc, dec, and maxSpeed of the speed profile."""

    address: str = field(default="/speedProfile", init=False)
    motorID: int
    """
    ========== ===========
    Controller Motor Range
    ========== ===========
    STEP400    1-4
    STEP800    1-8
    ========== ===========
    """
    acc: float
    """14.55-59590.0 steps/s/s"""
    dec: float
    """14.55-59590.0 stesp/s/s"""
    maxSpeed: float
    """15.25-15610.0 steps/s"""


@dataclass
class FullstepSpeed(OSCResponse):
    """The threshold when microstepping switches to full-step mode."""

    address: str = field(default="/fullstepSpeed", init=False)
    motorID: int
    """
    ========== ===========
    Controller Motor Range
    ========== ===========
    STEP400    1-4
    STEP800    1-8
    ========== ===========
    """
    fullstepSpeed: float
    """7.63-15625.0 steps/s"""


@dataclass
class MinSpeed(OSCResponse):
    """Minimum speed of the profile."""

    address: str = field(default="/minSpeed", init=False)
    motorID: int
    """
    ========== ===========
    Controller Motor Range
    ========== ===========
    STEP400    1-4
    STEP800    1-8
    ========== ===========
    """
    minSpeed: float
    """0.0-976.3 steps/s"""


@dataclass
class Speed(OSCResponse):
    """The current motor speed."""

    address: str = field(default="/speed", init=False)
    motorID: int
    """
    ========== ===========
    Controller Motor Range
    ========== ===========
    STEP400    1-4
    STEP800    1-8
    ========== ===========
    """
    speed: float
    """-15625.0-15625.0 steps/s"""


# Homing


@dataclass
class HomingDirection(OSCResponse):
    """The motor rotating direction when homing."""

    address: str = field(default="/homingDirection", init=False)
    motorID: int
    """
    ========== ===========
    Controller Motor Range
    ========== ===========
    STEP400    1-4
    STEP800    1-8
    ========== ===========
    """
    homingDirection: int
    """
    ===== ======================
    Range Description
    ===== ======================
    0-1   1: Forward, 0: Reverse
    ===== ======================
    """


@dataclass
class HomingSpeed(OSCResponse):
    """The speed the motor will run when homing."""

    address: str = field(default="/homingSpeed", init=False)
    motorID: int
    """
    ========== ===========
    Controller Motor Range
    ========== ===========
    STEP400    1-4
    STEP800    1-8
    ========== ===========
    """
    homingSpeed: float
    """0.0-15625.0 steps/s"""


@dataclass
class GoUntilTimeout(OSCResponse):
    """
    The timeout duration for the :py:class:`stepseries.commands.GoUntil`
    command.
    """

    address: str = field(default="/goUntilTimeout", init=False)
    motorID: int
    """
    ========== ===========
    Controller Motor Range
    ========== ===========
    STEP400    1-4
    STEP800    1-8
    ========== ===========
    """
    timeout: int
    """0.0-65535.0 ms"""


@dataclass
class ReleaseSwTimeout(OSCResponse):
    """
    The timeout duration for the
    :py:class:`stepseries.commands.ReleaseSw` command.
    """

    address: str = field(default="/releaseSwTimeout", init=False)
    motorID: int
    """
    ========== ===========
    Controller Motor Range
    ========== ===========
    STEP400    1-4
    STEP800    1-8
    ========== ===========
    """
    timeout: int
    """0.0-10000.0 ms"""


# Home and Limit Sensors


@dataclass
class SwEvent(OSCResponse):
    """Sent when the specified motor's HomeSw drops from HIGH to LOW."""

    address: str = field(default="/swEvent", init=False)
    motorID: int
    """
    ========== ===========
    Controller Motor Range
    ========== ===========
    STEP400    1-4
    STEP800    1-8
    ========== ===========
    """


@dataclass
class HomeSw(OSCResponse):
    """The status of the HomeSw, whether open or closed."""

    address: str = field(default="/homeSw", init=False)
    motorID: int
    """
    ========== ===========
    Controller Motor Range
    ========== ===========
    STEP400    1-4
    STEP800    1-8
    ========== ===========
    """
    swState: int
    """
    ===== =============================
    Range Description
    ===== =============================
    0-1   1: Open, 0: Closed (detected)
    ===== =============================
    """
    direction: int
    """
    ===== ======================
    Range Description
    ===== ======================
    0-1   1: Forward, 0: Reverse
    ===== ======================
    """


@dataclass
class LimitSw(OSCResponse):
    """The status of the LimitSw, whether open or closed."""

    address: str = field(default="/limitSw", init=False)
    motorID: int
    """
    ========== ===========
    Controller Motor Range
    ========== ===========
    STEP400    1-4
    STEP800    1-8
    ========== ===========
    """
    swState: int
    """
    ===== =============================
    Range Description
    ===== =============================
    0-1   1: Open, 0: Closed (detected)
    ===== =============================
    """
    direction: int
    """
    ===== ======================
    Range Description
    ===== ======================
    0-1   1: Forward, 0: Reverse
    ===== ======================
    """


@dataclass
class HomeSwMode(OSCResponse):
    """
    The switch mode as described in
    :py:class:`stepseries.commands.SetHomeSwMode.`
    """

    address: str = field(default="/homeSwMode", init=False)
    motorID: int
    """
    ========== ===========
    Controller Motor Range
    ========== ===========
    STEP400    1-4
    STEP800    1-8
    ========== ===========
    """
    swMode: int
    """
    ===== ================================================
    Range Description
    ===== ================================================
    0-1   1: HardStop interrupt, 0: Notification (no stop)
    ===== ================================================
    """


@dataclass
class LimitSwMode(OSCResponse):
    """
    The switch mode as described in
    :py:class:`stepseries.commands.SetHomeSwMode.`
    """

    address: str = field(default="/limitSwMode", init=False)
    motorID: int
    """
    ========== ===========
    Controller Motor Range
    ========== ===========
    STEP400    1-4
    STEP800    1-8
    ========== ===========
    """
    swMode: int
    """
    ===== ================================================
    Range Description
    ===== ================================================
    0-1   1: HardStop interrupt, 0: Notification (no stop)
    ===== ================================================
    """


# Position Management


@dataclass
class Position(OSCResponse):
    """The ABS_POS register value aka "the motor's current position"."""

    address: str = field(default="/position", init=False)
    motorID: int
    """
    ========== ===========
    Controller Motor Range
    ========== ===========
    STEP400    1-4
    STEP800    1-8
    ========== ===========
    """
    ABS_POS: int
    """-2,097,152-2,097,151 steps"""


@dataclass
class PositionList(OSCResponse):
    """The current position of all motors at once.

    STEP400 users: ``position5-8`` will be None since there are only
    four drivers on the board.
    """

    address: str = field(default="/positionList", init=False)
    position1: int
    """-2,097,152-2,097,151 steps"""
    position2: int
    """-2,097,152-2,097,151 steps"""
    position3: int
    """-2,097,152-2,097,151 steps"""
    position4: int
    """-2,097,152-2,097,151 steps"""
    position5: int = None
    """-2,097,152-2,097,151 steps"""
    position6: int = None
    """-2,097,152-2,097,151 steps"""
    position7: int = None
    """-2,097,152-2,097,151 steps"""
    position8: int = None
    """-2,097,152-2,097,151 steps"""


@dataclass
class ElPos(OSCResponse):
    """The electrical position of the motor."""

    address: str = field(default="/elPos", init=False)
    motorID: int
    """
    ========== ===========
    Controller Motor Range
    ========== ===========
    STEP400    1-4
    STEP800    1-8
    ========== ===========
    """
    fullstep: int
    """
    ===== =================
    Range Description
    ===== =================
    0-3   Fullstep position
    ===== =================
    """
    microstep: int
    """
    ===== ==================
    Range Description
    ===== ==================
    0-127 Microstep position
    ===== ==================
    """


@dataclass
class Mark(OSCResponse):
    """The latest MARK position."""

    address: str = field(default="/mark", init=False)
    motorID: int
    """
    ========== ===========
    Controller Motor Range
    ========== ===========
    STEP400    1-4
    STEP800    1-8
    ========== ===========
    """
    MARK: int
    """-2,097,152-2,097,151 steps"""


# Electromagnetic Brake


@dataclass
class BrakeTransitionDuration(OSCResponse):
    """The transitional duration when switching the brake mode."""

    address: str = field(default="/brakeTransitionDuration", init=False)
    motorID: int
    """
    ========== ===========
    Controller Motor Range
    ========== ===========
    STEP400    1-4
    STEP800    1-8
    ========== ===========
    """
    duration: int
    """0.0-10000.0 ms"""


# Servo Mode


@dataclass
class ServoParam(OSCResponse):
    """The PID control gain."""

    address: str = field(default="/servoParam", init=False)
    motorID: int
    """
    ========== ===========
    Controller Motor Range
    ========== ===========
    STEP400    1-4
    STEP800    1-8
    ========== ===========
    """
    kP: float
    """
    ===== =================
    Range Description
    ===== =================
    0.0-  Proportional gain
    ===== =================
    """
    kI: float
    """
    ===== =============
    Range Description
    ===== =============
    0.0-  Integral gain
    ===== =============
    """
    kD: float
    """
    ===== ===============
    Range Description
    ===== ===============
    0.0-  Derivative gain
    ===== ===============
    """
