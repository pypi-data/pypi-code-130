"""Command Module"""


class Command:
    """
    Converts the quantum gate operation into a specific command.

    Attributes:
        gate: quantum gate operator
        targets: target qubits
        controls: control qubits
        rotation: angle for rotation gate
    """

    def __init__(self, gate, targets, controls=[], rotation=[], inverse=False):
        # todo controls和rotation改成元组
        self.gate = gate
        self.controls = controls
        self.targets = targets
        self.rotation = rotation
        self.cmd_ver = "1.0"
        self.inverse = inverse

    def __eq__(self, other):
        """
        Two command are the same if they have teh same qasm.
        """
        if type(self) is not type(other):
            return False

        if self.qasm() == other.qasm():
            return True
        return False

    def __repr__(self) -> str:
        """Generate a representation of the command object instance

        Returns:
            str: A representation of the command instance
        """
        return f"Command(gate={self.gate}, controls={self.controls}, targets={self.targets}, rotation={self.rotation}), inverse={self.inverse})"

    def qasm(self):
        """
        generate OpenQASM code for command
        """
        name = str(self.gate).lower()

        if str(self.gate) == "Measure":
            index = self.targets[0]
            return f"{name} q[{str(index)}] -> c[{str(index)}]"

        ctrl_cnt = len(self.controls)
        if ctrl_cnt == 2:
            name = name.replace("c", "cc", 1)
        elif ctrl_cnt > 2:
            name = name.replace("c", "c" + str(ctrl_cnt), 1)

        angles_str = ""
        angles = self.gate.angles()
        if angles:
            angles_str = "(" + ",".join([str(ag) for ag in angles]) + ")"

        qubits_index = self.controls + self.targets
        qubits_str = ",".join([f"q[{qi}]" for qi in qubits_index])
        return name + angles_str + " " + qubits_str

    def quqasm(self):
        """
        generate QuQASM code for command
        """
        name = str(self.gate)
        params = []
        param_str = ""

        ctrl_cnt = len(self.controls)
        if ctrl_cnt > 1:
            params.append(ctrl_cnt)

        angles = self.gate.angles()
        if angles:
            params += angles

        if params:
            param_str = "(" + ", ".join([str(param) for param in params]) + ")"

        qubits_index = self.controls + self.targets
        qubits_str = ", ".join([f"q[{qi}]" for qi in qubits_index])
        if len(qubits_index) > 1:
            qubits_str = '(' + qubits_str + ')'

        return name + param_str + " * " + qubits_str

    @property
    def name(self):
        """command name"""
        return self.gate

    @property
    def num_qubits(self):
        """Return the number of qubits."""
        return len(self.controls) + len(self.targets)
