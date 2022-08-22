import can
from PyCanOpenDevice import CanOpen_Codes, CanOpen_Callbacks


class CanOpen_Arbitrier:
    def __init__(self, callback: CanOpen_Callbacks.CanOpen_Callbacks):
        self.callbacks: CanOpen_Callbacks.CanOpen_Callbacks = callback

    def can_open_arbitrier(self, message: can.Message):
        msg_arbitrier_id = message.arbitration_id

        if msg_arbitrier_id == CanOpen_Codes.SYNC:
            self.callbacks.sync(message)
        elif (msg_arbitrier_id > CanOpen_Codes.SDO_RX_BASE_ARB) and (msg_arbitrier_id <= CanOpen_Codes.SDO_RX_MAX_ARB):
            address = msg_arbitrier_id - CanOpen_Codes.SDO_RX_BASE_ARB
            self.callbacks.obj_recv(message, address, True, None)
        elif (msg_arbitrier_id > CanOpen_Codes.PDO1_RX_MIN) and (msg_arbitrier_id <= CanOpen_Codes.PDO1_RX_MAX):
            address = msg_arbitrier_id - CanOpen_Codes.PDO1_RX_MIN
            self.callbacks.obj_recv(message, address, False, 1)
        elif (msg_arbitrier_id > CanOpen_Codes.PDO2_RX_MIN) and (msg_arbitrier_id <= CanOpen_Codes.PDO2_RX_MAX):
            address = msg_arbitrier_id - CanOpen_Codes.PDO2_RX_MIN
            self.callbacks.obj_recv(message, address, False, 2)
        elif (msg_arbitrier_id > CanOpen_Codes.PDO3_RX_MIN) and (msg_arbitrier_id <= CanOpen_Codes.PDO3_RX_MAX):
            address = msg_arbitrier_id - CanOpen_Codes.PDO3_RX_MIN
            self.callbacks.obj_recv(message, address, False, 3)
        elif (msg_arbitrier_id > CanOpen_Codes.PDO4_RX_MIN) and (msg_arbitrier_id <= CanOpen_Codes.PDO4_RX_MAX):
            address = msg_arbitrier_id - CanOpen_Codes.PDO4_RX_MIN
            self.callbacks.obj_recv(message, address, False, 4)
