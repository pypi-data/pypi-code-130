import numpy as np

from qutrunk.circuit import Command
from .basicgate import BasicGate


class CYGate(BasicGate):
    """Control Y gate."""

    def __init__(self):
        super().__init__()

    def __str__(self):
        return "CY"

    def __or__(self, qubits):
        """
        Quantum logic gate operation

        Args:s
            qubits: qubits[0] is control qubit, qubits[1] is target qubit.

        Example:
            CY * (qr[0], qr[1])
        """
        if len(qubits) != 2:
            raise AttributeError("参数错误：应该传入1个控制位，1个目标位")
        self.qubits = qubits
        controls = [qubits[0].index]
        targets = [qubits[1].index]
        cmd = Command(self, targets, controls, inverse=self.is_inverse)
        qubits[0].circuit.append_cmd(cmd)

    def __mul__(self, qubits):
        """Overwrite * operator to achieve quantum logic gate operation, reuse __or__ operator implement"""
        self.__or__(qubits)

    @property
    def matrix(self):
        """Access to the matrix property of this gate."""
        return np.array(
            [[0, 0, -1j, 0], [0, 1, 0, 0], [1j, 0, 0, 0], [0, 0, 0, 1]]
        )


CY = CYGate()
