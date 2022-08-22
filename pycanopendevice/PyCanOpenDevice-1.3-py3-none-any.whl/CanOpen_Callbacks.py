import can
from PyCanOpenDevice import CanOpen_Device, CanOpen_BusActions
from PyCanOpenDevice.CanOpen_Codes import SDO_TX_BASE_ARB


class CanOpen_Callbacks:
    def __init__(self, bus_action: CanOpen_BusActions.CanOpen_BusActions):
        self.bus_action = bus_action
        self.services: list[CanOpen_Device.Device] = []

    def convert_int(self, value):
        return int.from_bytes(value, "little", signed=False)

    def add_service(self, service: CanOpen_Device.Device):
        self.bus_action.bootup_device(service.adress)
        service.set_sender(self.bus_action)
        self.services.append(service)

    def obj_recv(self, message: can.Message, id: int, is_sdo: bool, pdo_num: int):
        for service in self.services:
            if service.is_device(id):
                if is_sdo:
                    self.sdo_process_recv(service, message, id)
                else:
                    self.pdo_process_recv(service, message, id, pdo_num)
                break

    def sdo_process_recv(self, service: CanOpen_Device.Device, message: can.Message, id: int):

        domain = message.data[0]
        main_index = self.convert_int(message.data[1:3])
        sub_index = message.data[3]
        data = self.convert_int(message.data[4:])

        data_avb, data_to_send = service.process(domain, main_index, sub_index, data)

        if data_avb:
            self.bus_action.send_one(SDO_TX_BASE_ARB + id, data_to_send)

    def pdo_process_recv(self, service: CanOpen_Device.Device, message: can.Message, id: int, pdo_num):
        data = self.convert_int(message.data)
        service.process_pdo(data, message.data, pdo_num)

    def sync(self, msg: can.Message):
        for service in self.services:
            service.on_sync()
