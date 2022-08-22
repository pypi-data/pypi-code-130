from PyCanOpenDevice.CanOpen_Codes import PDO1_TX_MIN, PDO2_TX_MIN, PDO3_TX_MIN, PDO4_TX_MIN, \
    SLAVE_SUCCESSFUL_WRITE_RESPONSE


class SDO_Structure:
    def __init__(self, main_identifier: int, sub_identifier: int, function):
        self.main_identifier = main_identifier
        self.sub_identifier = sub_identifier
        self.function = function

    def processable(self, main_id: int, sub_id: int) -> bool:
        return main_id == self.main_identifier and sub_id == self.sub_identifier


class Device:
    def __init__(self, adress: int):
        self.sdos: list[SDO_Structure] = []
        self.adress = adress

        self.pdo1_callback = None
        self.pdo2_callback = None
        self.pdo3_callback = None
        self.pdo4_callback = None

        self.sender = None
        self.heartbeat_task = None

        self.pdo1_data = 0
        self.pdo2_data = 0
        self.pdo3_data = 0
        self.pdo4_data = 0

        self.add_sdo(SDO_Structure(0x1017, 0x00, self.handler_heartbeat))

    def handler_heartbeat(self, domain: int, data: int):
        heartbeat = data
        print(" -- Config Handler -- Heartbeat: " + str(heartbeat))
        try:
            self.heartbeat_task = self.sender.start_heartbeat_with_id_and_periode(self.adress, data)
        except:
            self.heartbeat_task.stop()
            self.heartbeat_task = self.sender.start_heartbeat_with_id_and_periode(self.adress, data)

            print(" -- Heardbeat allready set")
        return SLAVE_SUCCESSFUL_WRITE_RESPONSE, 0x00

    def generate_sdo_byte_array(self, domain: int, main_id: int, sub_id: int, data: int):
        byte_domain = domain.to_bytes(1, "little")
        byte_sub_id = sub_id.to_bytes(1, "little")
        byte_main_id = main_id.to_bytes(2, "little")
        byte_data = data.to_bytes(4, "big")

        return byte_domain + byte_main_id + byte_sub_id + byte_data

    def is_device(self, request_adress: int):
        return request_adress == self.adress

    def add_sdo(self, sdo_struct):
        self.sdos.append(sdo_struct)

    def set_sender(self, fun):
        self.sender = fun

    def set_pdo_data(self, pdo: int, data: int):
        if pdo == 1:
            self.pdo1_data = data
        elif pdo == 2:
            self.pdo2_data = data
        elif pdo == 3:
            self.pdo3_data = data
        elif pdo == 4:
            self.pdo4_data = data

    def call_sdo_function_and_send_back_result(self, domain: int, main_id: int, sub_id: int, data,
                                               function) -> bytearray:
        domain_response, data_response = function(domain, data)
        return self.generate_sdo_byte_array(domain_response, main_id, sub_id, data_response)

    def process(self, domain: int, main_id: int, sub_id: int, data: int):
        for curent_sdo in self.sdos:
            if curent_sdo.processable(main_id, sub_id):
                return True, self.call_sdo_function_and_send_back_result(domain, main_id, sub_id, data,
                                                                         curent_sdo.function)

        return False, 0

    def send_pdo(self, pdo: int):
        if pdo == 1:
            self.sender.send_one(PDO1_TX_MIN + self.adress, self.pdo1_data.to_bytes(4, "little"))
        elif pdo == 2:
            self.sender.send_one(PDO2_TX_MIN + self.adress, self.pdo2_data.to_bytes(4, "little"))
        elif pdo == 3:
            self.sender.send_one(PDO3_TX_MIN + self.adress, self.pdo3_data.to_bytes(4, "little"))
        elif pdo == 4:
            self.sender.send_one(PDO4_TX_MIN + self.adress, self.pdo4_data.to_bytes(4, "little"))

    def on_sync(self):
        self.send_pdo(1)

    def set_pdo_callback(self, number: int, fun):
        if number == 1:
            self.pdo1_callback = fun
        elif number == 2:
            self.pdo2_callback = fun
        elif number == 3:
            self.pdo3_callback = fun
        elif number == 4:
            self.pdo4_callback = fun

    def process_pdo(self, data: int, data_raw: bytearray, pdo_num: int):
        if self.pdo1_callback is not None and pdo_num == 1:
            self.pdo1_callback(data)
        elif self.pdo2_callback is not None and pdo_num == 2:
            self.pdo2_callback(data)
        elif self.pdo3_callback is not None and pdo_num == 3:
            self.pdo3_callback(data)
        elif self.pdo4_callback is not None and pdo_num == 4:
            self.pdo4_callback(data)
