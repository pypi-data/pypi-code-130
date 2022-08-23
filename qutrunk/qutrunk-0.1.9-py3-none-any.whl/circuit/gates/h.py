"""Hadamard gate."""

import cmath

import numpy as np

from qutrunk.circuit import Command
from .basicgate import BasicGate


class HGate(BasicGate):
    """
    Apply the single-qubit Hadamard gate
    """

    def __init__(self):
        super().__init__()

    def __str__(self):
        return "H"

    def __or__(self, qubit):
        """
        Quantum logic gate operation
        
        Args:
            qubit: quantum bit applied to hadamard gate
        Example:
            H * qr[0]
        """
        targets = [qubit.index]
        cmd = Command(self, targets, inverse=self.is_inverse)
        qubit.circuit.append_cmd(cmd)

    def __mul__(self, qubit):
        """Overwrite * operator to achieve quantum logic gate operation, reuse __or__ operator implement"""
        self.__or__(qubit)

    @property
    def matrix(self):
        """Access to the matrix property of this gate."""
        return 1.0 / cmath.sqrt(2.0) * np.matrix([[1, 1], [1, -1]])

    @property
    def label(self):
        """a label for identifying the gate."""
        self.__str__()


H = HGate()
