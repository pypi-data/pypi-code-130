import numpy as np

from qutrunk.circuit import Command
from .basicgate import BasicGate


class U1(BasicGate):
    """
    U1 gate
    """

    def __init__(self, alpha):
        """
        Args:
            alpha: rotation angle 
        """
        super().__init__()
        self.rotation = alpha

    def __str__(self):
        return "U1"

    def __or__(self, qubit):
        """
        Quantum logic gate operation

        Args:
            qubit: the quantum bit to apply U1 gate.

        Example:
            U1(pi/2) * qr[0]
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
        lam = float(self.rotation)
        return np.matrix([[1, 0], [0, np.exp(1j * lam)]])
