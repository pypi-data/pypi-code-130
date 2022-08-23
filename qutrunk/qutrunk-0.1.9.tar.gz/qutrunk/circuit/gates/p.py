import cmath

import numpy as np

from qutrunk.circuit import Command
from .basicgate import BasciPhaseGate


class P(BasciPhaseGate):
    """
    Phase gate (global phase)

    Args:
        alpha: the phase to apply
    """

    def __init__(self, alpha):
        super().__init__()
        self.rotation = alpha

    def __str__(self):
        return "P"

    def __or__(self, qubit):
        """
        Quantum logic gate operation

        Args:
            qubit: the quantum bit to aplly phase gate.

        Example:
            P(alpha) * qr[0]
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
        return np.matrix([[cmath.exp(1j * self.rotation), 0], [0, cmath.exp(1j * self.rotation)]])
