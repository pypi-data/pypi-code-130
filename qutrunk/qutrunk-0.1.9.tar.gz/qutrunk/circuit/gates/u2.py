import numpy as np

from qutrunk.circuit import Command
from .basicgate import BasicGate


class U2(BasicGate):
    """
    U2 gate
    """

    def __init__(self, theta, phi):
        """
        Args:
            theta: U2 gate parameter1
            phi: U2 gate parameter2
        """
        super().__init__()
        self.theta = theta
        self.phi = phi

    def __str__(self):
        return "U2"

    def __or__(self, qubit):
        """
        Quantum logic gate operation

        Args:
            qubit: the quantum bit to apply U2 gate.

        Example:
            U2(pi/2, pi/2) * qr[0]
        """
        targets = [qubit.index]
        cmd = Command(self, targets, rotation=[self.theta, self.phi], inverse=self.is_inverse)
        qubit.circuit.append_cmd(cmd)

    def __mul__(self, qubit):
        """Overwrite * operator to achieve quantum logic gate operation, \
            reuse __or__ operator implement"""
        self.__or__(qubit)

    @property
    def matrix(self):
        """Access to the matrix property of this gate."""
        isqrt2 = 1 / np.sqrt(2)
        phi = self.theta
        lam = self.phi
        return np.matrix(
            [
                [isqrt2, -np.exp(1j * lam) * isqrt2],
                [np.exp(1j * phi) * isqrt2, np.exp(1j * (phi + lam)) * isqrt2],
            ]
        )
