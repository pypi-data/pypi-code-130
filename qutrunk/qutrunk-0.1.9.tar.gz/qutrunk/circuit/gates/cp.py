# TODO:模块内统一包引用
import numpy as np

from qutrunk.circuit import Command
from .basicgate import BasicRotateGate


class CP(BasicRotateGate):
    """Control Phase Gate"""
    def __init__(self, angle):
        super().__init__()
        self.rotation = angle

    def __str__(self):
        return "CP"

    def __or__(self, qubits):
        """
        Quantum logic gate operation

        Args:
            qubits: qubits[0] is control qubit, qubits[1] is target qubit.

        Example:
            CP * (qr[0], qr[1])
        """
        if len(qubits) != 2:
            raise AttributeError("参数错误：应该传入1个控制位，1个目标位")
        self.qubits = qubits
        controls = [qubits[0].index]
        targets = [qubits[1].index]
        cmd = Command(self, targets, controls, rotation=[self.rotation], inverse=self.is_inverse)
        qubits[0].circuit.append_cmd(cmd)

    def __mul__(self, qubits):
        """Overwrite * operator to achieve quantum logic gate operation, reuse __or__ operator implement"""
        self.__or__(qubits)

    @property
    def matrix(self):
        """Access to the matrix property of this gate."""
        eith = np.exp(1j * float(self.rotation))
        return np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, eith, 0], [0, 0, 0, 1]])
