import cmath

import numpy as np

from qutrunk.circuit import Command
from .basicgate import BasicRotateGate


class Rz(BasicRotateGate):
    """
    Rotate a single qubit by a given angle around the Z-axis of the Bloch-sphere \
        (also known as a phase shift gate).

    Args:
        alpha: the angle to rotate
    """

    def __init__(self, alpha):
        super().__init__()
        self.rotation = alpha

    def __str__(self):
        return "Rz"

    def __or__(self, qubit):
        """
        Quantum logic gate operation

        Args:
            qubit: the quantum bit to aplly Rz gate.

        Example:
            Rz(alpha) * qr[0]
        """
        targets = [qubit.index]
        cmd = Command(self, targets, rotation=[self.rotation], inverse=self.is_inverse)
        qubit.circuit.append_cmd(cmd)

    def __mul__(self, qubit):
        """Overwrite * operator to achieve quantum logic gate operation, \
            reuse __or__ operator implement"""
        self.__or__(qubit)

    @property
    def matrix(self):
        """Access to the matrix property of this gate."""
        return np.matrix(
            [
                [cmath.exp(-0.5 * 1j * self.rotation), 0],
                [0, cmath.exp(0.5 * 1j * self.rotation)],
            ]
        )
