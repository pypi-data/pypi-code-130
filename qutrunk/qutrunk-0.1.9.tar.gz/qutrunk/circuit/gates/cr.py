import numpy as np

from qutrunk.circuit import Command
from .basicgate import BasicRotateGate


class CR(BasicRotateGate):
    """Control rotation gate"""
    def __init__(self, alpha):
        """
        Args:
            alpha: rotation angle
        """
        super().__init__()
        self.rotation = alpha

    def __str__(self):
        return "CR"

    def __or__(self, qubits):
        """
        Quantum logic gate operation

        Args:
            qubit: the quantum bit to aplly CR gate

        Example:
            CR(pi/2) * (qr[0], qr[1])
        """
        if len(qubits) != 2:
            raise AttributeError("Parameter Error: qubits should be two")
        self.qubits = qubits
        controls = [qubits[0].index]
        targets = [qubits[1].index]
        cmd = Command(self, targets, controls, inverse=self.is_inverse, rotation=[self.rotation])
        qubits[0].circuit.append_cmd(cmd)

    def __mul__(self, qubits):
        """Overwrite * operator to achieve quantum logic gate operation, reuse __or__ operator implement"""
        self.__or__(qubits)

    @property
    def matrix(self):
        """Access to the matrix property of this gate."""
        half_alpha = float(self.rotation)
        return np.matrix([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, np.exp(1j * half_alpha)]])
