import platform

from qutrunk.tools.function_time import timefn
try:
    from qutrunk.sim.local import simulator
except ImportError:  # pragma: no cover
    # windows 
    from qutrunk.sim.local.Release import simulator


class BackendLocalCpp:
    """ Simulator is a compiler engine which simulates a quantum computer using C++-based kernels."""
    @timefn
    def init(self, qubits, state, value, show):
        return simulator.init(qubits, state, value, show)

    @timefn
    def send_circuit(self, circuit, final):
        """
        Send the quantum circuit to local backend

        Args:
            circuit: quantum circuit to send
            final: True if quantum circuit finish, default False, \
                when final==True The backend program will release the computing resources
        """
        start = circuit.cmd_cursor
        cmds = circuit.cmds[start:]
        temp_cmds = []
        for cmd in cmds:
            tempCmd = simulator.Cmd()
            tempCmd.gate = str(cmd.gate)
            tempCmd.targets = cmd.targets
            tempCmd.controls = cmd.controls
            tempCmd.rotation = cmd.rotation
            tempCmd.desc = cmd.qasm()
            tempCmd.inverse = cmd.inverse
            temp_cmds.append(tempCmd)

        simulator.send_circuit(temp_cmds, final)
        # start = circuit.cmd_cursor
        # stop = len(circuit.cmds)
        # for idx in range(start, stop):
        #     cmd = circuit.cmds[idx]
        #     res = simulator.execCmd(gate=str(cmd.gate),
        #                             targets=cmd.targets,
        #                             controls=cmd.controls,
        #                             rotation=cmd.rotation,
        #                             desc=cmd.qasm)

        #     if str(cmd.gate) == "Measure":
        #         qubit = cmd.targets[0]
        #         circuit.qreg[qubit].cbit = res

    @timefn
    def run(self, shots):
        return simulator.run(shots)

    @timefn
    def get_prob_amp(self, index):
        """
        Get the probability of a state-vector at an index in the full state vector.

        Args:
            index: index in state vector of probability amplitudes

        Returns:
            the probability of target index
        """
        return simulator.getProbOfAmp(index)

    @timefn
    def get_prob_outcome(self, qubit, outcome):
        """
        Get the probability of a specified qubit being measured in the given outcome (0 or 1)

        Args:
            qubit: the specified qubit to be measured
            outcome: the qubit measure result(0 or 1)

        Returns:
            the probability of target qubit 
        """
        return simulator.getProbOfOutcome(qubit, outcome)

    @timefn
    def get_prob_all_outcome(self, qubit):
        """
        Get outcomeProbs with the probabilities of every outcome of the sub-register contained in qureg

        Args:
            qubits: the sub-register contained in qureg

        Returns:
            An array contains probability of target qubits
        """
        return simulator.getProbOfAllOutcome(qubit)

    @timefn
    def get_all_state(self):
        """
        Get the current state vector of probability amplitudes for a set of qubits
        """
        return simulator.getAllState()

    @timefn
    def apply_QFT(self, qubits):
        """
        Applies the quantum Fourier transform (QFT) to a specific subset of qubits of the register qureg

        Args:
            qubits: a list of the qubits to operate the QFT upon
        """
        return simulator.apply_QFT(qubits)

    @timefn
    def apply_Full_QFT(self):
        """
        Applies the quantum Fourier transform (QFT) to the entirety of qureg
        """
        return simulator.apply_Full_QFT()