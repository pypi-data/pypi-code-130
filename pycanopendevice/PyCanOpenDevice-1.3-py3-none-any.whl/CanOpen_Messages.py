import can

from PyCanOpenDevice import CanOpen_Codes


def get_bootupMessage(can_id: int) -> can.Message:
    return can.Message(arbitration_id=CanOpen_Codes.NMT_ERROR_CONTROL_BASE_ARB + can_id,
                       data=[0x00],
                       is_extended_id=False)

def getHeartbeatMessage(can_id: int) -> can.Message:
    return can.Message(arbitration_id=CanOpen_Codes.NMT_ERROR_CONTROL_BASE_ARB + can_id,
                       data=[0x05],
                       is_extended_id=False)
