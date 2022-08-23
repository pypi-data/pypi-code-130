from qutrunk.circuit.ops.operation import Pauli, PauliType


class PauliZ(Pauli):
    """Apply the PauliZ"""

    def __init__(self, *targets):
        super().__init__(list(targets), PauliType.POT_PAULI_Z)
