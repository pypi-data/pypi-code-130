import numpy as np

from qutrunk.circuit import Command
from .basicgate import BasicGate


class X1Gate(BasicGate):
    """Apply the single-qubit X1 gate"""

    def __init__(self):
        super().__init__()

    def __str__(self):
        return "X1"

    def __or__(self, qubit):
        """
        Quantum logic gate operation

        Args:
            qubit: the quantum bit to aplly X1 gate
        Example:
            X1 * qr[0]
        """
        targets = [qubit.index]
        cmd = Command(self, targets, inverse=self.is_inverse)
        qubit.circuit.append_cmd(cmd)

    def __mul__(self, qubit):
        """Overwrite * operator to achieve quantum logic gate operation, \
            reuse __or__ operator implement"""
        self.__or__(qubit)

    @property
    def matrix(self):
        """Access to the matrix property of this gate."""
        factor = 1 / np.sqrt(2)
        return np.matrix([[factor, -1j * factor], [-1j * factor, factor]])


X1 = X1Gate()
