import can

from PyCanOpenDevice import CanOpen_Receiver, CanOpen_Callbacks, CanOpen_BusActions, CanOpen_Arbitrier


class CanOpen_Runtime:
    def __init__(self, bus: can.Bus):
        self.heartbeat_task = None
        self.bus_actions = CanOpen_BusActions.CanOpen_BusActions(bus)
        self.callbacks = CanOpen_Callbacks.CanOpen_Callbacks(self.bus_actions)
        self.arbitrier = CanOpen_Arbitrier.CanOpen_Arbitrier(self.callbacks)
        self.receiver = CanOpen_Receiver.CanOpen_Receiver(bus, self.arbitrier)

