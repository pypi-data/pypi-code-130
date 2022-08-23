from qutrunk.circuit.ops.operation import Pauli, PauliType


class PauliX(Pauli):
    """Apply the PauliX"""

    def __init__(self, *targets):
        super().__init__(list(targets), PauliType.POT_PAULI_X)
