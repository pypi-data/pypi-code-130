import numpy as np

from qutrunk.circuit import Command
from .basicgate import BasicGate


class SGate(BasicGate):
    """Apply the single-qubit S gate"""

    def __init__(self):
        super().__init__()

    def __str__(self):
        return "S"

    def __or__(self, qubit):
        """
        Quantum logic gate operation

        Args:
            qubit: the quantum bit to apply S gate.

        Example:
            S * qr[0]
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
        return np.matrix([[1, 0], [0, 1j]])


S = SGate()
