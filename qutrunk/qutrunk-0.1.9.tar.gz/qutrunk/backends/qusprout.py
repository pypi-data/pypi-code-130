from enum import Enum
from qutrunk.sim.qusprout.rpcclient import QuSproutApiServer
from qutrunk.sim.qusprout.qusproutdata import ttypes as qusproutdata
from qutrunk.tools.read_qubox import get_qubox_setting
from .backend import Backend


class ExecType(Enum):
    """
    Init exec type for quantum circuit

    Attributes:
        ExecBySingleProcess: Execute by single process
        ExecByMpi: Execute by multiple processes
    """
    SingleProcess = 1
    Mpi = 2


class BackendQuSprout(Backend):
    """
    QuSprout: quamtum circuit simulator, provide multi-threaded OMP, multi node parallel MPI, GPU hardware acceleration.
    To use qusprout, make sure the network is connected and the service IP and Port are set correctly.
    """
    def __init__(self, exectype=ExecType.SingleProcess):
        super().__init__()
        self.circuit = None
        self.exectype = exectype
        box_config = get_qubox_setting()
        self._api_server = QuSproutApiServer(ip=box_config.get('ip'), port=box_config.get('port'))

    def get_prob_amp(self, index):
        """
        Get the probability of a state-vector at an index in the full state vector

        Args:
            index: index in state vector of probability amplitudes

        Returns:
            the probability of target index
        """
        res, elapsed = self._api_server.get_prob_amp(index)
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
        res, elapsed = self._api_server.get_prob_all_outcome(qubits)
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
        res, elapsed = self._api_server.get_prob_outcome(qubit, outcome)
        if self.circuit.counter:
            self.circuit.counter.acc_run_time(elapsed)
        return res

    def get_all_state(self):
        """
        Get the current state vector of probability amplitudes for a set of qubits
        """
        res, elapsed = self._api_server.get_all_state()
        if self.circuit.counter:
            self.circuit.counter.acc_run_time(elapsed)
        return res

    def send_circuit(self, circuit, final=False):
        """
        Send the quantum circuit to qusprout backend

        Args:
            circuit: quantum circuit to send
            final: True if quantum circuit finish, default False, \
                when final==True The backend program will release the computing resources 
        """
        cmds = []
        start = circuit.cmd_cursor
        stop = len(circuit.cmds)

        for idx in range(start, stop):
            cmd = circuit.cmds[idx]
            c = qusproutdata.Cmd(str(cmd.gate), cmd.targets, cmd.controls, cmd.rotation, cmd.qasm(), cmd.inverse)
            cmds.append(c)

        circuit.forward(stop - start)

        # 服务端初始化
        if start == 0:
            res, elapsed = self._api_server.init(
                circuit.qubits_len, 
                circuit.initstate, 
                circuit.initvalue,
                circuit.get_density(),
                self.exectype.value)
            if self.circuit.counter:
                self.circuit.counter.acc_run_time(elapsed)

        if len(cmds) == 0 and (not final):
            return

        # 发送至服务        
        res, elapsed = self._api_server.send_circuit(qusproutdata.Circuit(cmds), final)
        if self.circuit.counter:
            self.circuit.counter.acc_run_time(elapsed)

    def run(self, shots=1):
        """
        Run quantum circuit

        Args:
            shots: circuit run times, for sampling, default: 1
        
        Returns:
            result: the Result object contain circuit running outcome
        """
        res, elapsed = self._api_server.run(shots)
        if self.circuit.counter:
            self.circuit.counter.acc_run_time(elapsed)
            self.circuit.counter.finish() 

        """
        1 必须释放连接，不然其它连接无法连上服务端
        2 不能放在__del__中，因为对象释放不代表析构函数会及时调用
        """
        self._api_server.close()

        return res

    def apply_QFT(self, qubits):
        """
        Applies the quantum Fourier transform (QFT) to a specific subset of qubits of the register qureg

        Args:
            qubits: a list of the qubits to operate the QFT upon
        """
        self._api_server.apply_QFT(qubits)

    def apply_Full_QFT(self):
        """
        Applies the quantum Fourier transform (QFT) to the entirety of qureg
        """
        self._api_server.apply_Full_QFT()

    def get_expec_pauli_prod(self, pauli_prod_list):
        """
        Computes the expected value of a product of Pauli operators.

        Args:
            pauli_prod_list: a list contains the indices of the target qubits,\
                the Pauli codes (0=PAULI_I, 1=PAULI_X, 2=PAULI_Y, 3=PAULI_Z) to apply to the corresponding qubits.

        Returns:
            the expected value of a product of Pauli operators.
        """
        puali_list = []
        for temp in pauli_prod_list:
            puali_list.append(qusproutdata.PauliProdInfo(temp['oper_type'], temp['target']))
            
        res, elapsed = self._api_server.get_expec_pauli_prod(puali_list)
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
        res, elapsed = self._api_server.get_expec_pauli_sum(oper_type_list, term_coeff_list)
        if self.circuit.counter:
            self.circuit.counter.acc_run_time(elapsed)
        return res
