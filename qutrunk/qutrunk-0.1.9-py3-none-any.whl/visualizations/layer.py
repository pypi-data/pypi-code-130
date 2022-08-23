"""A layer is the column of the circuit."""
from .text_draw_element import (
    BoxOnQuWireTop,
    BoxOnQuWireMid,
    BoxOnClWireMid,
    BoxOnClWireBot,
    BoxOnClWire,
    BoxOnClWireTop,
    BoxOnQuWire,
    BoxOnQuWireBot,
    Bullet,
    OpenBullet,
)
from qutrunk.circuit import CBit, CReg, QuBit


class Layer:
    """a layer is the column of the circuit."""
    def __init__(self, qubits, cbits, circuit=None):
        # QuBit对象列表
        self.qubits = qubits
        # CBit对象列表
        self.cbits = cbits
        # 量子电路
        self.circuit = circuit
        # 量子层数
        self.qubit_layer = [None] * len(qubits)
        # 连接
        self.connections = []
        # 经典比特层数
        self.cbit_layer = [None] * len(cbits)

    @property
    def full_layer(self):
        """
        Returns the composition of qubits and classic wires.
        """
        return self.qubit_layer + self.cbit_layer

    def set_qubit(self, qubit, element):
        """Sets the qubit to the element.
        Args:
            qubit: Element of self.qubits.
            element: Element to draw.
        """
        self.qubit_layer[self.qubits.index(qubit)] = element

    def set_cbit(self, cbit, element):
        """Sets the cbit to the element."""
        self.cbit_layer[self.cbits.index(cbit)] = element

    def _set_multibox(self, label, qubits=None, cbits=None, top_connect=None, bot_connect=None, conditional=False, controlled_edge=None):
        # qubits和cbits都不空
        if qubits is not None and cbits is not None:
            # 获取cbits元素的下标
            cbit_index = sorted(i for i, x in enumerate(self.cbits) if x in cbits)
            # 获取qubits元素的下标
            qbit_index = sorted(i for i, x in enumerate(self.qubits) if x in qubits)

            # 使用元素下标做label，找到最长的下标长度
            wire_label_len = max(len(str(len(qubits) - 1)), len(str(len(cbits) - 1)))

            # 返回qubit下标的左对齐字符串列表
            qargs = [
                str(qubits.index(qbit)).ljust(wire_label_len, " ")
                for qbit in self.qubits
                if qbit in qubits
            ]
            # 返回cbit下标的左对齐字符串列表
            cargs = [
                str(cbits.index(cbit)).ljust(wire_label_len, " ")
                for cbit in self.cbits
                if cbit in cbits
            ]
            # 按照index排序
            qubits = sorted(qubits, key=self.qubits.index)
            cbits = sorted(cbits, key=self.cbits.index)

            # box的高度
            box_height = len(self.qubits) - min(qbit_index) + max(cbit_index) + 1

            # 量子比特
            # 设置顶部元素
            self.set_qubit(qubits.pop(0), BoxOnQuWireTop(label, wire_label=qargs.pop(0)))
            order = 0
            for order, bit_i in enumerate(range(min(qbit_index) + 1, len(self.qubits))):
                if bit_i in qbit_index:
                    named_bit = qubits.pop(0)
                    wire_label = qargs.pop(0)
                else:
                    named_bit = self.qubits[bit_i]
                    wire_label = " " * wire_label_len
                # 设置中间部分元素
                self.set_qubit(
                    named_bit, BoxOnQuWireMid(label, box_height, order, wire_label=wire_label)
                )

            # 经典比特
            for order, bit_i in enumerate(range(max(cbit_index)), order + 1):
                if bit_i in cbit_index:
                    named_bit = cbits.pop(0)
                    wire_label = cargs.pop(0)
                else:
                    named_bit = self.cbits[bit_i]
                    wire_label = " " * wire_label_len
                self.set_cbit(
                    named_bit, BoxOnClWireMid(label, box_height, order, wire_label=wire_label)
                )
            self.set_cbit(
                cbits.pop(0), BoxOnClWireBot(label, box_height, wire_label=cargs.pop(0))
            )
            return cbit_index

        # qubits是空的，但cbits不空
        if qubits is None and cbits is not None:
            bits = list(cbits)
            bit_index = sorted(i for i, x in enumerate(self.cbits) if x in bits)
            wire_label_len = len(str(len(bits) - 1))
            bits.sort(key=self.cbits.index)
            qargs = [""] * len(bits)
            set_bit = self.set_cbit
            OnWire = BoxOnClWire
            OnWireTop = BoxOnClWireTop
            OnWireMid = BoxOnClWireMid
            OnWireBot = BoxOnClWireBot
        # cbits是空的，但qubits不空
        elif cbits is None and qubits is not None:
            bits = list(qubits)
            bit_index = sorted(i for i, x in enumerate(self.qubits) if x in bits)
            wire_label_len = len(str(len(bits) - 1))
            qargs = [
                str(bits.index(qbit)).ljust(wire_label_len, " ")
                for qbit in self.qubits
                if qbit in bits
            ]
            bits.sort(key=self.qubits.index)
            set_bit = self.set_qubit
            OnWire = BoxOnQuWire
            OnWireTop = BoxOnQuWireTop
            OnWireMid = BoxOnQuWireMid
            OnWireBot = BoxOnQuWireBot
        else:
            raise ValueError("_set_multibox error.")

        control_index = {}
        if controlled_edge:
            for index, qubit in enumerate(self.qubits):
                for qubit_in_edge, value in controlled_edge:
                    if qubit == qubit_in_edge:
                        control_index[index] = "■" if value == "1" else "o"

        if len(bit_index) == 1:
            set_bit(bits[0], OnWire(label, top_connect=top_connect))
        else:
            box_height = max(bit_index) - min(bit_index) + 1
            set_bit(bits.pop(0), OnWireTop(label, top_connect=top_connect, wire_label=qargs.pop(0)))

            for order, bit_i in enumerate(range(min(bit_index) + 1, max(bit_index))):
                if bit_i in bit_index:
                    named_bit = bits.pop(0)
                    wire_label = qargs.pop(0)
                else:
                    named_bit = (self.qubits + self.cbits)[bit_i]
                    wire_label = " " * wire_label_len

                control_label = control_index.get(bit_i)
                set_bit(
                    named_bit,
                    OnWireMid(
                        label, box_height, order, wire_label=wire_label, control_label=control_label
                    ),
                )

            set_bit(
                bits.pop(0),
                OnWireBot(
                    label,
                    box_height,
                    bot_connect=bot_connect,
                    wire_label=qargs.pop(0),
                    conditional=conditional,
                ),
            )
        return bit_index

    def set_qu_multibox(self, bits, label, top_connect=None, bot_connect=None, conditional=False, controlled_edge=None):
        """Sets the multi qubit box."""
        return self._set_multibox(
            label,
            qubits=bits,
            top_connect=top_connect,
            bot_connect=bot_connect,
            conditional=conditional,
            controlled_edge=controlled_edge,
        )

    def connect_with(self, wire_char):
        """Connects the elements in the layer using wire_char."""
        if len([qbit for qbit in self.qubit_layer if qbit is not None]) == 1:
            return None

        for label, affected_bits in self.connections:

            if not affected_bits:
                continue

            affected_bits[0].connect(wire_char, ["bot"])
            for affected_bit in affected_bits[1:-1]:
                affected_bit.connect(wire_char, ["bot", "top"])

            affected_bits[-1].connect(wire_char, ["top"], label)

            if label:
                for affected_bit in affected_bits:
                    affected_bit.right_fill = len(label) + len(affected_bit.mid)
                    if isinstance(affected_bit, (Bullet, OpenBullet)) and affected_bit.conditional:
                        affected_bit.left_fill = len(label) + len(affected_bit.mid)

    def set_cl_multibox(self, condition, top_connect="┴"):
        """set multi cbit box"""
        pass


def get_condition_label_val(condition, circuit, cregbundle=True, reverse_bits=False):
    """
    Get the label and value list to display a condition
    """
    cond_is_bit = bool(isinstance(condition[0], CBit))
    cond_val = int(condition[1])

    if isinstance(condition[0], CReg) and not cregbundle:
        val_bits = list(f"{cond_val:0{condition[0].size}b}")
        if not reverse_bits:
            val_bits = val_bits[::-1]
    else:
        val_bits = list(str(cond_val))

    label = ""
    if cond_is_bit and cregbundle:
        register, _, reg_index = get_bit_reg_index(circuit, condition[0], False)
        if register is not None:
            label = f"{register.name}_{reg_index}={hex(cond_val)}"
    elif not cond_is_bit:
        label = hex(cond_val)

    return label, val_bits


# TODO:doing
def get_bit_reg_index(circuit, bit, reverse_bits):
    # 获取bit的下标
    bit_index = circuit.find_bit(bit)
    reg_index = bit_index
    # 获取对应寄存器
    if isinstance(bit, QuBit):
        register = circuit.qreg[bit]

    if isinstance(bit, CBit):
        register = circuit.creg[bit]

    return register, bit_index, reg_index