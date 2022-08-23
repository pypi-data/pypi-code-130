"""
Classical register reference object.
"""
import itertools

from .classical_bit import CBit


class CReg:
    """A classical register."""

    prefix = "c"
    bit_type = "CBit"
    instances_counter = itertools.count()

    def __init__(self, circuit=None, name=None, size=None):
        if name is None:
            name = f"{self.prefix}{self.instances_counter}"
        self.name = name

        self.cbits = []
        # 寄存器大小
        self.size = size
        self.circuit = circuit

        for index in range(self.size):
            self.cbits.append(CBit(self, index))

    def append(self, cbit):
        """add a CBit instance"""
        self.cbits.append(cbit)

    def qasm(self):
        """Return OPENQASM string for this register."""
        return f"creg {self.name}[{self.size}];"

    def __getitem__(self, idx):
        """return a Cbit instance.

        Args:
            idx: the index of Cbit.
            
        Returns:
            Cbit instance
        """
        if not isinstance(idx, int):
            raise ValueError("expected integer index into register")
        return self.cbits[idx]

    def __len__(self):
        return len(self.cbits)

    def index(self, cbit):
        """Find the index of the provided cbit within this register."""
        return self.cbits.index(cbit)

    def __setitem__(self, key, value):
        self.cbits[key] = value

    def __repr__(self):
        return f"{self.__class__.__qualname__}({self.size})"
