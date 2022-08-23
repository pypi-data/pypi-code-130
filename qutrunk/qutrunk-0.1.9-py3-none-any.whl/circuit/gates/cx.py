import numpy as np

from qutrunk.circuit import Command
from .basicgate import BasicGate


class MCX(BasicGate):
    """Multi-control X(NOT) gate"""
    def __init__(self, ctrl_cnt=1):
        super().__init__()
        self.ctrl_cnt = ctrl_cnt

    def __str__(self):
        return "CX"

    def __or__(self, qubits):
        """
        Quantum logic gate operation

        Args:
            qubits: the left self.ctrl_cnt qubits are control qubits, the rest right bits are target qubits.

        Example:
            MCX(2) * (qr[0], qr[1], qr[2]) # qr[0], qr[1] are control qubits, qr[2] is target qubit
            MCX(3) * (qr[0], qr[1], qr[2], qr[3])
        """
        self.qubits = qubits
        controls = [q.index for q in qubits[0:self.ctrl_cnt]]
        targets = [q.index for q in qubits[self.ctrl_cnt:]]
        cmd = Command(self, targets, controls, inverse=self.is_inverse)
        qubits[0].circuit.append_cmd(cmd)

    def __mul__(self, qubits):
        """Overwrite * operator to achieve quantum logic gate operation, reuse __or__ operator implement"""
        self.__or__(qubits)

    @property
    def matrix(self):
        """Access to the matrix property of this gate."""
        if self.ctrl_cnt == 1:
            return np.array(
                [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]]
            )


CX = CNOT = MCX(1)
Toffoli = MCX(2)
