from pymodbus.payload import BinaryPayloadDecoder

class PayloadDecoder(BinaryPayloadDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def decode(self, modbus_type: str, byte_count: int):
        if modbus_type == 'INT16':
            return self.decode_16bit_int()
        elif modbus_type == 'INT16u':
            return self.decode_16bit_uint()
        elif modbus_type == 'INT32':
            return self.decode_32bit_int()
        elif modbus_type == 'INT32u':
            return self.decode_32bit_uint()
        elif modbus_type == 'INT64':
            return self.decode_64bit_int()
        elif modbus_type == 'INT64u':
            return self.decode_64bit_uint()
        elif modbus_type == 'FLOAT32':
            return self.decode_32bit_float()
        elif modbus_type == 'FLOAT64':
            return self.decode_32bit_float()
        elif modbus_type == 'STRING':
            return self.decode_string(byte_count)
        else:
            pass