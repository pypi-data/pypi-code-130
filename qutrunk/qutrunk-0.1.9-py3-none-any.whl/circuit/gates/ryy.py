import cmath

import numpy as np

from qutrunk.circuit import Command
from .basicgate import BasicRotateGate


class Ryy(BasicRotateGate):
    """
    RotationYY gate class

    Args:
        alpha: the angle to rotate
    """

    def __init__(self, alpha):
        super().__init__()
        self.rotation = alpha

    def __str__(self):
        return "Ryy"

    def __or__(self, qubits):
        """
        Quantum logic gate operation

        Args:
            qubits: the quantum bits to apply Ryy gate.

        Example:
            Ryy(alpha) * (qr[0], qr[1])
        """
        if len(qubits) != 2:
            raise AttributeError()
        targets = [q.index for q in qubits]
        cmd = Command(self, targets, rotation=[self.rotation], inverse=self.is_inverse)
        qubits[0].circuit.append_cmd(cmd)

    def __mul__(self, qubits):
        """Overwrite * operator to achieve quantum logic gate operation, reuse __or__ operator implement"""
        self.__or__(qubits)

    @property
    def matrix(self):
        """Access to the matrix property of this gate."""
        return np.matrix(
            [
                [cmath.cos(0.5 * self.rotation), 0, 0, 1j * cmath.sin(0.5 * self.rotation)],
                [0, cmath.cos(0.5 * self.rotation), -1j * cmath.sin(0.5 * self.rotation), 0],
                [0, -1j * cmath.sin(0.5 * self.rotation), cmath.cos(0.5 * self.rotation), 0],
                [1j * cmath.sin(0.5 * self.rotation), 0, 0, cmath.cos(0.5 * self.rotation)],
            ]
        )
