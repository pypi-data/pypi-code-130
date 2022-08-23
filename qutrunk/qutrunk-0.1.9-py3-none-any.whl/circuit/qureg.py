import itertools

from .qubit import QuBit


class Qureg:
    """
    Qubit register, maintains a set of qubits.

    Arg:
        name: The name of the register.
        qubits: a list which store Qubit instance
    """
    prefix = "q"
    bit_type = "QuBit"
    instances_counter = itertools.count()

    def __init__(self, circuit=None, name=None, size=None):
        if name is None:
            name = f"{self.prefix}{self.instances_counter}"
        self.name = name

        self.qubits = []
        # 寄存器大小
        self.size = size
        self.circuit = circuit

        for index in range(self.size):
            self.qubits.append(QuBit(self, index))

    def __getitem__(self, idx):
        """return a Qubit instance.
        Arg:
            idx: the index of Qubit.
        Returns:
            Qubit instance
        """
        if not isinstance(idx, int):
            raise ValueError("expected integer index into register")
        return self.qubits[idx]

    def __len__(self):
        return len(self.qubits)

    def qasm(self):
        """Return OPENQASM string for this register."""
        return f"qreg q[{len(self)}];"

    def __repr__(self):
        return f"{self.__class__.__qualname__}({self.size})"

    def index(self, qubit):
        """Find the index of the provided qubit within this register."""
        return self.qubits.index(qubit)





