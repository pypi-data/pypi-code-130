from qutrunk.circuit.ops.operation import Pauli, PauliType


class PauliI(Pauli):
    """Apply the PauliI"""
    def __init__(self, *targets):
        super().__init__(list(targets), PauliType.POT_PAULI_I)
