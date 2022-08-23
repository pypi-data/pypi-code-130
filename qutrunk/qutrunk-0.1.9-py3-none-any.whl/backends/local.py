from qutrunk.backends.backend import Backend

from qutrunk.tools.read_qubox import get_qulocalbox_setting

try:
    from qutrunk.sim.local.local_cpp import BackendLocalCpp as BackendLocalImpl
except ImportError:
    from qutrunk.sim.local.local_python import BackendLocalPython as BackendLocalImpl

from enum import Enum

class BackendLocalType(Enum):
    """Backend Local Type"""

    CPP = 0
    PYTHON = 1
    UNKNOWN = 2

class BackendLocal(Backend):
    """
    The local backend uses the simulator to run the quantum circuit, qutrunk provide two types simulator.
    C++ simulator is preferred. If C++ simulator is not available, python simulator is used instead
    """
    def __init__(self):
        super().__init__()
        self.circuit = None
        self._local_impl = BackendLocalImpl()
        box_config = get_qulocalbox_setting()
        self._show_quantum_gate = box_config.get('show_quantum_gate')

    def send_circuit(self, circuit, final=False):
        """
        Send the quantum circuit to local backend

        Args:
            circuit: quantum circuit to send
            final: True if quantum circuit finish, default False, \
                when final==True The backend program will release the computing resources 
        """
        start = circuit.cmd_cursor
        stop = len(circuit.cmds)

        if start == 0:
            res, elapsed = self._local_impl.init(
                len(circuit.qreg), 
                circuit.initstate, 
                circuit.initvalue,
                self._show_quantum_gate)
            if self.circuit.counter:
                self.circuit.counter.acc_run_time(elapsed)

        res, elapsed = self._local_impl.send_circuit(circuit, final)
        if self.circuit.counter:
            self.circuit.counter.acc_run_time(elapsed)

        circuit.forward(stop - start)

        return res

    def run(self, shots=1):
        """
        Run quantum circuit

        Args:
            shots: circuit run times, for sampling, default: 1
        
        Returns:
            result: the Result object contain circuit running outcome
        """
        res, elapsed = self._local_impl.run(shots)
        if self.circuit.counter:
            self.circuit.counter.acc_run_time(elapsed)
            self.circuit.counter.finish()
        return res

    def get_prob_amp(self, index):
        """
        Get the probability of a state-vector at an index in the full state vector

        Args:
            index: index in state vector of probability amplitudes

        Returns:
            the probability of target index
        """
        res, elapsed = self._local_impl.get_prob_amp(index)
        if self.circuit.counter:
            self.circuit.counter.acc_run_time(elapsed)
        return res

    def get_prob_outcome(self, qubit, outcome):
        """
        Get the probability of a specified qubit being measured in the given outcome (0 or 1)

        Args:
            qubit: the specified qubit to be measured
            outcome: the qubit measure result(0 or 1)

        Returns:
            the probability of target qubit
        """
        res, elapsed = self._local_impl.get_prob_outcome(qubit, outcome)
        if self.circuit.counter:
            self.circuit.counter.acc_run_time(elapsed)
        return res

    def get_prob_all_outcome(self, qubits):
        """
        Get outcomeProbs with the probabilities of every outcome of the sub-register contained in qureg

        Args:
            qubits: the sub-register contained in qureg

        Returns:
            An array contains probability of target qubits
        """
        res, elapsed = self._local_impl.get_prob_all_outcome(qubits)
        if self.circuit.counter:
            self.circuit.counter.acc_run_time(elapsed)
        return res

    def get_all_state(self):
        """
        Get the current state vector of probability amplitudes for a set of qubits
        """
        res, elapsed = self._local_impl.get_all_state()
        if self.circuit.counter:
            self.circuit.counter.acc_run_time(elapsed)
        return res

    def apply_QFT(self, qubits):
        """
        Applies the quantum Fourier transform (QFT) to a specific subset of qubits of the register qureg

        Args:
            qubits: a list of the qubits to operate the QFT upon
        """
        res, elapsed = self._local_impl.apply_qft(qubits)
        if self.circuit.counter:
            self.circuit.counter.acc_run_time(elapsed)
        return res

    def apply_Full_QFT(self):
        """
        Applies the quantum Fourier transform (QFT) to the entirety of qureg
        """
        res, elapsed = self._local_impl.apply_full_qft()
        if self.circuit.counter:
            self.circuit.counter.acc_run_time(elapsed)
        return res

    def get_expec_pauli_prod(self, pauli_prod_list):
        """
        Computes the expected value of a product of Pauli operators.

        Args:
            pauli_prod_list: a list contains the indices of the target qubits,\
                the Pauli codes (0=PAULI_I, 1=PAULI_X, 2=PAULI_Y, 3=PAULI_Z) to apply to the corresponding qubits.

        Returns:
            the expected value of a product of Pauli operators.
        """
        res, elapsed = self._local_impl.get_expec_pauli_prod(pauli_prod_list)
        if self.circuit.counter:
            self.circuit.counter.acc_run_time(elapsed)
        return res
    
    def get_expec_pauli_sum(self, oper_type_list, term_coeff_list):
        """
        Computes the expected value of a sum of products of Pauli operators.

        Args:
            oper_type_list: a list of the Pauli codes (0=PAULI_I, 1=PAULI_X, 2=PAULI_Y, 3=PAULI_Z) \
                of all Paulis involved in the products of terms. A Pauli must be specified \
                for each qubit in the register, in every term of the sum.
            term_coeff_list: the coefficients of each term in the sum of Pauli products.

        Returns:
            the expected value of a sum of products of Pauli operators. 
        """
        res, elapsed = self._local_impl.get_expec_pauli_sum(oper_type_list, term_coeff_list)
        if self.circuit.counter:
            self.circuit.counter.acc_run_time(elapsed)
        return res

    def get_local_type(self):
        """
        return which local is being used
        """
        if type(self._local_impl) == BackendLocalCpp:
            return BackendLocalType.CPP
        elif type(self._local_impl) == BackendLocalPython:
            return BackendLocalType.PYTHON
        else:
            return BackendLocalType.UNKNOWN