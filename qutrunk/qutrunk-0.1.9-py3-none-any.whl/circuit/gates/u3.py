import numpy as np

from qutrunk.circuit import Command
from .basicgate import BasicGate


class U3(BasicGate):
    """
    U3 gate
    """

    def __init__(self, theta, phi, lam):
        """
        Args:
            theta: U3 gate parameter1
            phi: U3 gate parameter2
            lam: U3 gate parameter3
        """
        super().__init__()
        self.theta = theta
        self.phi = phi
        self.lam = lam

    def __str__(self):
        return "U3"

    def __or__(self, qubit):
        """
        Quantum logic gate operation

        Args:
            qubit: the quantum bit to apply U3 gate.

        Example:
            U3(pi/2,pi/2,pi/2) * qr[0]
        """
        targets = [qubit.index]
        cmd = Command(self, targets, rotation=[self.theta, self.phi, self.lam], inverse=self.is_inverse)
        qubit.circuit.append_cmd(cmd)

    def __mul__(self, qubit):
        """Overwrite * operator to achieve quantum logic gate operation, \
            reuse __or__ operator implement"""
        self.__or__(qubit)

    @property
    def matrix(self):
        """Access to the matrix property of this gate."""
        theta = self.theta
        phi = self.phi
        lam = self.lam
        cos = np.cos(theta / 2)
        sin = np.sin(theta / 2)
        return np.array(
            [
                [cos, -np.exp(1j * lam) * sin],
                [np.exp(1j * phi) * sin, np.exp(1j * (phi + lam)) * cos],
            ]
        )


class U(U3):
    pass
