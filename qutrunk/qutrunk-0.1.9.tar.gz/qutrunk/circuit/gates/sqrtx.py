import numpy as np

from qutrunk.circuit import Command
from .basicgate import BasicGate


class SqrtXGate(BasicGate):
    """Square-root X gate class."""

    def __init__(self):
        super().__init__()

    def __str__(self):
        return "SqrtX"

    def __or__(self, qubit):
        """
        Quantum logic gate operation

        Args:
            qubit: the quantum bit to apply SqrtX gate.

        Example:
            SqrtX * qr[0]
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
        return 0.5 * np.matrix([[1 + 1j, 1 - 1j], [1 - 1j, 1 + 1j]])


SqrtX = SqrtXGate()
