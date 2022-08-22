import can

from PyCanOpenDevice import CanOpen_Arbitrier


class CanOpen_Receiver:

    def __init__(self, bus: can.Bus, arb: CanOpen_Arbitrier.CanOpen_Arbitrier):
        self.arb = arb
        self.bus = bus

    def recv_loop(self):
        while 1:
            msg = self.bus.recv()
            #print("--Message-- ID: " + str(msg.arbitration_id) + str(msg.data))
            self.arb.can_open_arbitrier(msg)
