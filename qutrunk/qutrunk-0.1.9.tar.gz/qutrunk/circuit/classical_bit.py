from .bit import Bit


class CBit(Bit):
    """Implement a classical bit."""

    def __init__(self, creg=None, index=None, value=None):
        """Creates a classical bit."""
        super().__init__(creg, index)
        # value保存测量的值
        self.value = value
        if creg is not None:
            self.circuit = creg.circuit

    def set_value(self, value):
        """Update cbit value when the corresponding qubit measure done"""
        self.value = value
