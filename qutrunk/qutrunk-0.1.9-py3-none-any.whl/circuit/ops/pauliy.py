from qutrunk.circuit.ops.operation import Pauli, PauliType


class PauliY(Pauli):
    """Apply the PauliY"""

    def __init__(self, *targets):
        super().__init__(list(targets), PauliType.POT_PAULI_Y)
