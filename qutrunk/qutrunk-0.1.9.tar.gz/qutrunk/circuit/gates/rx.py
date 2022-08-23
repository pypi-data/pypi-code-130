import math

import numpy as np

from qutrunk.circuit import Command
from .basicgate import BasicRotateGate


class Rx(BasicRotateGate):
    """
    Rotate a single qubit by a given angle around the X-axis of the Bloch-sphere

    Args:
        alpha: the angle to rotate
    """

    def __init__(self, alpha):
        super().__init__()
        self.rotation = alpha

    def __str__(self):
        return "Rx"

    def __or__(self, qubit):
        """
        Quantum logic gate operation

        Args:
            qubit: the quantum bit to aplly Rx gate。

        Example:
            Rx(alpha) * qr[0]
        """
        targets = [qubit.index]
        cmd = Command(self, targets, rotation=[self.rotation], inverse=self.is_inverse)
        qubit.circuit.append_cmd(cmd)

    def __mul__(self, qubit):
        """Overwrite * operator to achieve quantum logic gate operation, reuse __or__ operator implement"""
        self.__or__(qubit)

    @property
    def matrix(self):
        """Access to the matrix property of this gate."""
        return np.matrix(
            [
                [math.cos(0.5 * self.rotation), -1j * math.sin(0.5 * self.rotation)],
                [-1j * math.sin(0.5 * self.rotation), math.cos(0.5 * self.rotation)],
            ]
        )
