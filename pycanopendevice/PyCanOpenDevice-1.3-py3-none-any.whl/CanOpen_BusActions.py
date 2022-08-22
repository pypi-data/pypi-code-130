import can
from PyCanOpenDevice import CanOpen_Messages


class CanOpen_BusActions:
    def __init__(self, bus: can.Bus):
        self.bus = bus

    def send_one_with_message_object(self, message: can.Message):
        try:
            self.bus.send(message)
            print("Message sent on {}".format(self.bus.channel_info))
        except can.CanError:
            print("Message NOT sent")

    def send_one(self, id: int, data: bytearray):
        msg = can.Message(arbitration_id=id,
                          data=data,
                          is_extended_id=False)

        self.send_one_with_message_object(msg)

    def bootup_device(self, id):
        self.send_one_with_message_object(CanOpen_Messages.get_bootupMessage(id))

    def start_heartbeat_with_id_and_periode(self, id: int, periode: int) -> can.broadcastmanager.CyclicSendTaskABC:
        return self.bus.send_periodic(period=periode/1000, msg=CanOpen_Messages.getHeartbeatMessage(id))
