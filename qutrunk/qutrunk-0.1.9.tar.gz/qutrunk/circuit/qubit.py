from .bit import Bit


class QuBit(Bit):
    """
    a quantum bit

    Attributes:
        circuit: A quantum circuit.
        index: The index of the bit in its containing register.
    """

    def __init__(self, qreg=None, index=None):
        """Creates a quantum bit."""
        super().__init__(qreg, index)
        if qreg is not None:
            self.circuit = qreg.circuit
