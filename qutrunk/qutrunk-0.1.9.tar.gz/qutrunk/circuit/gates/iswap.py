import numpy as np

from qutrunk.circuit import Command
from .basicgate import BasicGate


class iSwap(BasicGate):
    """Performs a iSWAP gate between qubit1 and qubit2"""

    def __init__(self, alpha):
        """
        Args:
            alpha: rotation angle
        """
        super().__init__()
        self.rotation = alpha

    def __str__(self):
        return "iSwap"

    def __or__(self, qubits):
        """
        Quantum logic gate operation

        Args:
            qubit: the quantum bit to aplly iSwap gate
        Example:
            iSwap(pi/2) * (qr[0], qr[1])
        """
        if len(qubits) != 2:
            raise AttributeError("Parameter Error: qubits should be two")
        self.qubits = qubits
        targets = [q.index for q in qubits]
        cmd = Command(self, targets, inverse=self.is_inverse, rotation=[self.rotation])
        qubits[0].circuit.append_cmd(cmd)

    def __mul__(self, qubits):
        """Overwrite * operator to achieve quantum logic gate operation, reuse __or__ operator implement"""
        self.__or__(qubits)

    @property
    def matrix(self):
        """Access to the matrix property of this gate."""
        half_alpha = float(self.rotation)
        cos = np.cos(half_alpha)
        sin = np.sin(half_alpha)
        return np.matrix([[1, 0, 0, 0], [0, cos, -1j * sin, 0], [0, -1j * sin, cos, 0], [0, 0, 0, 1]])
