import numpy as np

from qutrunk.circuit import Command
from .basicgate import BasicGate


class SwapGate(BasicGate):
    """Performs a SWAP gate between qubit1 and qubit2"""

    def __init__(self):
        super().__init__()

    def __str__(self):
        return "Swap"

    def __or__(self, qubits):
        """
        Quantum logic gate operation

        Args:
            qubits: qubits to swap.

        Example:
            Swap * (qr[0], qr[1])
        """
        targets = [q.index for q in qubits]
        cmd = Command(self, targets, inverse=self.is_inverse)
        qubits[0].circuit.append_cmd(cmd)

    def __mul__(self, qubits):
        """Overwrite * operator to achieve quantum logic gate operation, \
            reuse __or__ operator implement"""
        self.__or__(qubits)

    @property
    def matrix(self):
        """Access to the matrix property of this gate."""
        return np.matrix([[1, 0, 0, 0],
                          [0, 0, 1, 0],
                          [0, 1, 0, 0],
                          [0, 0, 0, 1]])


Swap = SwapGate()
