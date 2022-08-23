import can
import time
import cantools
import os
import sys
from cantools.database.can.signal import NamedSignalValue

'''
Please Define Board to test here !!!!
'''
dac_setpoints = dac_setpoints = [-1, -1, -1, -1, -1, -1, -1, -1]  # 8 DAC Channels

dac_mapping = {0: 9,
               1: 1,
               2: 5,
               3: 3,
               4: 4,
               5: 5,
               6: 6,
               7: 7}  # DAC Channel : Message Channel


class SignalCardController:
    """
    Base class to control all signal card relays inside a HiL
    """

    def __init__(self, dbc_dir):
        self.can0 = None
        self.can_db = cantools.database.Database()
        self.dbc_dir = dbc_dir
        print(f"Searching for DBCs in {self.dbc_dir}")
        for file in os.listdir(self.dbc_dir):
            if file.endswith(".dbc"):
                print(f"adding {file}")
                self.can_db.add_dbc_file(os.path.join(os.getcwd(), self.dbc_dir + file))

    def can_connection(self, interface, channel, bitrate):
        """
        Establishes a CAN connection
        :return:
        """
        # Usage with PEAK CAN Dongle
        can.rc['interface'] = interface
        can.rc['channel'] = channel
        can.rc['bitrate'] = bitrate
        self.can0 = can.interface.Bus()
        self.can0.flush_tx_buffer()  # Reset transmit after start

    def send_can_message(self, msg_name, commands):
        try:
            cmd_message = self.can_db.get_message_by_name(msg_name)
        except Exception as e:
            print(f"ERROR: Message {msg_name} not found in Databases")
            print(e)
            return None

        # prepare a message with all signals
        signals = {}
        for signal in cmd_message.signals:
            if signal.name in commands:
                signals[signal.name] = commands[signal.name]
            else:
                signals[signal.name] = 0

        message = can.Message(arbitration_id=cmd_message.frame_id,
                              data=cmd_message.encode(signals, strict=False),
                              is_extended_id=False)
        # print(f"sending message {message}")
        self.can0.send(message)

    @staticmethod
    def print_bin(num):
        x = []
        for b in num:
            x.append(bin(b))
        print(x)

    @staticmethod
    def create_payload(card_id, relay_data):
        """
        This will create a list with 8 Databytes (Total 64 Bits) to control HiL Cards
        Datastructure is as follows: (one based)
        Bit 1-4 -> Card ID
        Bit 5-64 -> Relay Data
        """
        out = [0] * 8
        out[0] = out[0] | (card_id & 0xF)
        out[0] = out[0] | (relay_data & 0xF) << 4
        for i in range(7):
            out[i + 1] = out[i + 1] | ((relay_data >> (i * 8) + 4) & 0xFF)
        return out

    def set_dac_value(self, channel, value):
        """Short summary.
        creates a can message out of the  dac state and sends it to the can connector

        CAN Message is DAC_BMS_Cntrl , ID 0x220
        Be aware of a weird channel mapping
        """
        dac_setpoints[channel] = value
        cmd = {}
        # Generate Signal name DAC_BMS_Cntrl_XX_YY_Voltage
        channel_msg = dac_mapping[channel] - 1
        dac_no = str(channel_msg // 4 + 1).zfill(2)  # Calculate Dac index, each dac has 4 channels
        ch_no = str((channel_msg % 4) + 1).zfill(2)  # channel is mod 4, both have to be filled to two digits
        mux = (0x10 * (channel_msg // 4)) + (channel_msg % 4)  # mux is 0-3 + 0x10 after each 4 channels
        cmd = {'DAC_BMS_Cntrl_Channel': mux, f"DAC_BMS_Cntrl_{dac_no}_{ch_no}_Voltage": value}
        # print(cmd)
        self.send_can_message("DAC_BMS_Cntrl", cmd)

    def send_relay_can_message(self, card, data):
        mux_name = "RC_cntrl" + str(card).zfill(2)
        cmd = {'RC_mux': card, mux_name: data}
        self.send_can_message("RC_Cntrl", cmd)

    def send_relay_can_message_raw(self, card, data):
        message = can.Message(arbitration_id=528,
                              data=self.create_payload(card, data),
                              is_extended_id=False)
        self.can0.send(message)

    def send_cmb_relay_can_message(self, cell, type, val):
        cmd = {f'RCCMBCntrl_CV{cell}_{type}': val}
        self.send_can_message("RCCMBCntrl", cmd)

    def check_card(self, card, relays=None):
        if card > 16:
            print(f"Card not there: {card}")
            return None
        if relays is None:
            max_relays = [32, 32, 32, 32, 48, 48, 32]  # max relays of cards
            relays = range(max_relays[card])
        if card == 4:  # analog card also set dac
            for ch in range(8):
                self.set_dac_value(ch, 2)
        for relay_no in relays:
            rly_set = 1 << (relay_no)
            print(f"Setting Card {card}, relay {relay_no}")
            print(bin(rly_set))
            self.send_relay_can_message_raw(card, rly_set)
            time.sleep(0.5)
            self.send_relay_can_message_raw(card, 0)
            time.sleep(0.1)

    def test_standard_signal_card1(self):
        used_ports = list(range(15)) + list(range(16, 31))  # zero based
        self.check_card(1, used_ports)

    def test_standard_signal_card2(self):
        used_ports = list(range(15)) + list(range(16, 31))  # zero based
        self.check_card(2, used_ports)

    def test_standard_signal_card3(self):
        used_ports = list(range(15)) + list(range(16, 31))  # zero based
        self.check_card(3, used_ports)

    def test_standard_signal_card4(self):
        used_ports = list(range(15)) + list(range(16, 31))  # zero based
        self.check_card(4, used_ports)

    def test_analog_signal_card(self):
        used_ports = list(range(32)) + list(range(32, 39)) + list(range(40, 48))  # zero based
        self.check_card(4, used_ports)

    def test_bus_signal_card(self):
        used_ports = list(range(3 * 16))  # zero based
        self.check_card(5, used_ports)

    def test_lb_contactor_card(self):
        used_ports = list(range(21))  # zero based
        self.check_card(9, used_ports)

    def test_cell_fault_board(self):
        for cell in range(18):
            print(f"Testing Open Circuit on cell {cell}")
            self.send_cmb_relay_can_message(cell, "OC", 1)
            time.sleep(0.5)
            self.send_cmb_relay_can_message(cell, "OC", 0)
            time.sleep(0.1)

        for cell in range(18):
            print(f"Testing High Impedance on cell {cell}")
            self.send_cmb_relay_can_message(cell, "HImp", 1)
            time.sleep(0.5)
            self.send_cmb_relay_can_message(cell, "HImp", 0)
            time.sleep(0.1)

    def test_card(self, card):
        funcs = {
            "AnalogSignal": self.test_analog_signal_card,
            "StandardSignal1": self.test_standard_signal_card1,
            "StandardSignal2": self.test_standard_signal_card2,
            "StandardSignal3": self.test_standard_signal_card3,
            "StandardSignal4": self.test_standard_signal_card4,
            "BusSignal": self.test_bus_signal_card,
            "CellFault": self.test_cell_fault_board,
            "LoadboxContactorCard": self.test_lb_contactor_card
        }
        if card in funcs:
            print(f"TESTING BOARD {card}")
            funcs[card]()
        else:
            raise Exception(f"Signal Card {card} not present.")

#####################
##  Main Function  ##
#####################
# if __name__ == '__main__':
# args = sys.argv
# if args and len(args) > 1 and args[1] == "-c":
#     BOARD_TO_TEST = args[2]
# testing = SignalCardController()
# funcs = {
#     "AnalogSignal": testing.test_analog_signal_card,
#     "StandardSignal1": testing.test_standard_signal_card1,
#     "StandardSignal2": testing.test_standard_signal_card2,
#     "StandardSignal3": testing.test_standard_signal_card3,
#     "StandardSignal4": testing.test_standard_signal_card4,
#     "BusSignal": testing.test_bus_signal_card,
#     "CellFault": testing.test_cell_fault_board,
#     "LoadboxContactorCard": testing.test_lb_contactor_card
# }
#
# print(f"TESTING BOARD {BOARD_TO_TEST}")
# funcs[BOARD_TO_TEST]()
