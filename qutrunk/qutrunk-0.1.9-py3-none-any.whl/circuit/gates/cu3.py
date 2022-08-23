import numpy as np

from qutrunk.circuit import Command
from .basicgate import BasicRotateGate


class CU3(BasicRotateGate):
    """
    Control U3 gate
    """

    def __init__(self, theta, phi, lam):
        """
        Args:
            theta: U3 gate parameter 1
            phi: U3 gate parameter 2
            lam: U3 gate parameter 3
        """
        super().__init__()
        self.theta = theta
        self.phi = phi
        self.lam = lam

    def __str__(self):
        return "CU3"

    def __or__(self, qubits):
        """
        Quantum logic gate operation

        Args:
            qubit: the quantum bit to aplly CU3 gate

        Example:
            CU3(pi/2,pi/2,pi/2) * (qr[0], qr[1])
        """

        if len(qubits) != 2:
            raise AttributeError("Parameter Error: qubits should be two")
        self.qubits = qubits
        controls = [qubits[0].index]
        targets = [qubits[1].index]
        cmd = Command(self, targets, controls, inverse=self.is_inverse, rotation=[self.theta, self.phi, self.lam])
        qubits[0].circuit.append_cmd(cmd)

    def __mul__(self, qubits):
        """Overwrite * operator to achieve quantum logic gate operation, reuse __or__ operator implement"""
        self.__or__(qubits)

    @property
    def matrix(self):
        """Access to the matrix property of this gate."""
        half_alpha = float(self.theta)
        half_beta = float(self.phi)
        half_theta = float(self.lam)
        cos = np.cos(half_alpha / 2)
        sin = np.sin(half_alpha / 2)
        return np.array(
            [
                [1, 0, 0, 0],
                [0, cos, 0, -np.exp(1j * half_theta) * sin],
                [0, 0, 1, 0],
                [0, np.exp(1j * half_beta) * sin, 0, np.exp(1j * (half_beta + half_theta)) * cos],
            ]
        )
