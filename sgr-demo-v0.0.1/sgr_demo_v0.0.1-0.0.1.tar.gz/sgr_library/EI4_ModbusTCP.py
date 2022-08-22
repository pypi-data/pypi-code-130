from payload_decoder import PayloadDecoder
from pymodbus.constants import Endian
from pymodbus.client.sync import ModbusTcpClient, ModbusSerialClient


# In this case establishes a connection with the localhost server that is running the simulation.
class ModbusConnect:

    def __init__(self, ip, port) -> None:
        #EXAMPLE: client = ModbusTcpClient('127.0.0.1', 5002)
        self.client = ModbusTcpClient(ip, port)
        self.client.connect()

    def value_decoder(self, addr, size):
        reg = self.client.read_input_registers(addr, size)
        #reg2 = self.client.read_input_registers(addr, 6) To read all registers at the same time for example ;)

        # Manage byteorder types only being BigEndian and LittleEndian.
        decoder = PayloadDecoder.fromRegisters(reg.registers, byteorder=Endian.Big, wordorder=Endian.Big)
        
        if not reg.isError():
            #print(reg.registers)
            return decoder.decode('FLOAT32', 0)