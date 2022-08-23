class BasicGate:
    """Base class of all gates. (Don't use it directly but derive from it).

    Args:
        is_inverse: Tells whether to inverse gate or not.
    """

    def __init__(self):
        self.is_inverse = False
        self.name = ""

    def __str__(self):
        """The string description of a quantum logic gate"""
        return ""

    def __or__(self, qubit):
        """Quantum logic gate operation. Overwrite | operator to achieve quantum logic gate operation"""
        pass

    def __mul__(self, qubits):
        """Overwrite * operator to achieve quantum logic gate operation, reuse __or__ operator implement"""
        pass

    def angles(self):
        """Get angle Args"""
        ANGLE_PARAMS = ('rotation', 'theta', 'phi', 'lam', 'gamma')
        return [getattr(self, param) for param in ANGLE_PARAMS if hasattr(self, param)]


class BasicRotateGate(BasicGate):
    """
    Base class for rotation gate
    """

    def __init__(self):
        super().__init__()


class BasciPhaseGate(BasicGate):
    """
    Base class for phase gate
    """

    def __init__(self):
        super().__init__()


class All(BasicGate):
    """
    Meta operator, provides unified operation of multiple qubits

    Args:
        gate: the gate will apply to all qubits
    """

    def __init__(self, gate):
        self.gate = gate

    def __or__(self, qureg):
        """
        Quantum logic gate operation

        Args:
            qureg: the qureg(represent a set of qubit) to apply gate.

        Example:
            All(H) * qureg
            All(Measure) * qureg
        """
        for q in qureg:
            self.gate | q

    def __mul__(self, qureg):
        """
        Args:
            qureg: the qureg(represent a set of qubit) to apply gate.

        Example:
            All(H) * qureg, All(Measure) * qureg
        """
        for q in qureg:
            self.gate * q


def Inv(gate):
    """
    Inverse gate.

    Args:
        gate: the gate will apply inverse operator

    Example:
        Inv(H) * q[0]
    """
    if isinstance(gate, BasicGate):
        gate.is_inverse = True

    return gate
