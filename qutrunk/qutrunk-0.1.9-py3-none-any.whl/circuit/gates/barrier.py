from qutrunk.circuit.qubit import QuBit
from qutrunk.circuit.command import Command
from .basicgate import BasicGate


class BarrierGate(BasicGate):
    """Barrier Gate"""

    def __init__(self):
        super().__init__()

    def __str__(self):
        return "Barrier"

    def __or__(self, qubits):
        """
        Quantum logic gate operation

        Args:
            qubits: the quantum bit to aplly Barrier gate.

        Example:
            Barrier * (qr[0], qr[1])
        """
        templist = [qubits] if isinstance(qubits, QuBit) else qubits
        targets = [q.index for q in templist]
        cmd = Command(self, targets)
        templist[0].circuit.append_cmd(cmd)

    def __mul__(self, qubits):
        """Overwrite * operator to achieve quantum logic gate operation, reuse __or__ operator implement"""
        self.__or__(qubits)

    @property
    def label(self):
        """Return gate label"""
        return "Barrier"


Barrier = BarrierGate()
