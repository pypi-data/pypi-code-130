import numpy as np

from qutrunk.circuit import Command
from .basicgate import BasicRotateGate


class CU(BasicRotateGate):
    """
    Control U gate
    """

    def __init__(self, theta, phi, lam, gamma):
        """
        Args:
            theta: U gate parameter 1
            phi: U gate parameter 2
            lam:U gate parameter 3
            gamma: U gate parameter 4
        """
        super().__init__()
        self.theta = theta
        self.phi = phi
        self.lam = lam
        self.gamma = gamma

    def __str__(self):
        return "CU"

    def __or__(self, qubits):
        """
        Quantum logic gate operation

        Args:
            qubit: the quantum bit to aplly CU gate
            
        Example:
            CU(pi/2,pi/2,pi/2,pi/2) * (qr[0], qr[1])
        """

        if len(qubits) != 2:
            raise AttributeError("Parameter Error: qubits should be two")
        self.qubits = qubits
        controls = [qubits[0].index]
        targets = [qubits[1].index]
        cmd = Command(self, targets, controls,
                      inverse=self.is_inverse, rotation=[self.theta, self.phi, self.lam, self.gamma])
        qubits[0].circuit.append_cmd(cmd)

    def __mul__(self, qubits):
        """Overwrite * operator to achieve quantum logic gate operation, reuse __or__ operator implement"""
        self.__or__(qubits)

    @property
    def matrix(self):
        """Access to the matrix property of this gate."""
        half_theta = float(self.theta)
        half_phi = float(self.phi)
        half_lam = float(self.lam)
        half_gamma = float(self.gamma)
        cos = np.cos(half_theta / 2)
        sin = np.sin(half_theta / 2)
        a = np.exp(1j * half_gamma) * cos
        b = -np.exp(1j * (half_gamma + half_lam)) * sin
        c = np.exp(1j * (half_gamma + half_phi)) * sin
        d = np.exp(1j * (half_gamma + half_phi + half_lam)) * cos
        return np.array(
            [
                [1, 0, 0, 0],
                [0, a, 0, b],
                [0, 0, 1, 0],
                [0, c, 0, d],
            ]
        )
