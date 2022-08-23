import uuid
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol, TMultiplexedProtocol

from qutrunk.sim.qusprout.qusprout import QuSproutServer
from qutrunk.sim.qusprout.work import WorkServer

from qutrunk.sim.qusprout.qusproutdata import ttypes as qusproutdata

from qutrunk.tools.function_time import timefn

class WorkApiServer:
    def __init__(self, ip='localhost', port=9090):
        socket = TSocket.TSocket(ip, port)
        self._transport = TTransport.TBufferedTransport(socket)
        protocol = TBinaryProtocol.TBinaryProtocol(self._transport)
        quest = TMultiplexedProtocol.TMultiplexedProtocol(protocol, "WorkServer")
        self._client = WorkServer.Client(quest)
        self._taskid = uuid.uuid4().hex
        self._transport.open()

    def close(self):
        self._transport.close()

    @timefn
    def init(self, qubits, state, value, density, exectype=0):
        req = qusproutdata.InitQubitsReq(self._taskid, qubits, state, value, density, exectype)
        return self._client.initQubits(req)

    @timefn
    def send_circuit(self, circuit, final):
        req = qusproutdata.SendCircuitCmdReq(self._taskid, circuit, final)
        res = self._client.sendCircuitCmd(req)
        return res

    @timefn
    def run(self, shots):
        req = qusproutdata.RunCircuitReq(self._taskid, shots)
        res = self._client.run(req)
        return res.result

    @timefn
    def get_prob_amp(self, index):
        """
        Get the probability of a state-vector at an index in the full state vector.

        Args:
            index: index in state vector of probability amplitudes

        Returns:
            the probability of target index
        """
        req = qusproutdata.GetProbAmpReq(self._taskid, index)
        res = self._client.getProbAmp(req)
        return res.amp

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
        req = qusproutdata.GetProbOfOutcomeReq(self._taskid, qubit, outcome)
        res = self._client.getProbOfOutcome(req)
        return res.pro_outcome

    @timefn
    def get_prob_all_outcome(self, qubits):
        """
        Get outcomeProbs with the probabilities of every outcome of the sub-register contained in qureg

        Args:
            qubits: the sub-register contained in qureg

        Returns:
            An array contains probability of target qubits
        """
        req = qusproutdata.GetProbOfAllOutcomReq(self._taskid, qubits)
        res = self._client.getProbOfAllOutcome(req)
        return res.pro_outcomes

    @timefn
    def get_all_state(self):
        """
        Get the current state vector of probability amplitudes for a set of qubits
        """
        req = qusproutdata.GetAllStateReq(self._taskid)
        res = self._client.getAllState(req)
        return res.all_state

    @timefn
    def cancel_Cmd(self):
        req = qusproutdata.CancelCmdReq(self._taskid)
        return self._client.cancelCmd(req)

    @timefn
    def apply_QFT(self, qubits):
        """
        Applies the quantum Fourier transform (QFT) to a specific subset of qubits of the register qureg

        Args:
            qubits: a list of the qubits to operate the QFT upon
        """
        req = qusproutdata.ApplyQFTReq(self._taskid, qubits)
        res = self._client.applyQFT(req)

    @timefn
    def apply_Full_QFT(self):
        """
        Applies the quantum Fourier transform (QFT) to the entirety of qureg
        """
        req = qusproutdata.ApplyFullQFTReq(self._taskid)
        res = self._client.applyFullQFT(req)

    @timefn
    def get_expec_pauli_prod(self, paulilist):
        """
        Computes the expected value of a product of Pauli operators.

        Args:
            pauli_prod_list: a list contains the indices of the target qubits,\
                the Pauli codes (0=PAULI_I, 1=PAULI_X, 2=PAULI_Y, 3=PAULI_Z) to apply to the corresponding qubits.

        Returns:
            the expected value of a product of Pauli operators.
        """
        req = qusproutdata.GetExpecPauliProdReq(self._taskid, paulilist)
        res = self._client.getExpecPauliProd(req)
        return res
    
    @timefn
    def get_expec_pauli_sum(self, paulilist):
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
        req = qusproutdata.GetExpecPauliSumReq(self._taskid, paulilist)
        res = self._client.getExpecPauliSum(req)
        return res
    
class QuSproutApiServer:
    def __init__(self, ip='localhost', port=9090):
        socket = TSocket.TSocket(ip, port)
        self._transport = TTransport.TBufferedTransport(socket)
        protocol = TBinaryProtocol.TBinaryProtocol(self._transport)
        quest = TMultiplexedProtocol.TMultiplexedProtocol(protocol, "QuSproutServer")
        self._client = QuSproutServer.Client(quest)
        self._taskid = uuid.uuid4().hex
        self._transport.open()

    def close(self):
        self._transport.close()

    @timefn
    def init(self, qubits, state, value, density, exectype=0):
        req = qusproutdata.InitQubitsReq(self._taskid, qubits, state, value, density, exectype)
        return self._client.initQubits(req)

    @timefn
    def send_circuit(self, circuit, final):
        req = qusproutdata.SendCircuitCmdReq(self._taskid, circuit, final)
        res = self._client.sendCircuitCmd(req)
        return res

    @timefn
    def run(self, shots):
        req = qusproutdata.RunCircuitReq(self._taskid, shots)
        res = self._client.run(req)
        return res.result

    @timefn
    def get_prob_amp(self, index):
        """
        Get the probability of a state-vector at an index in the full state vector.

        Args:
            index: index in state vector of probability amplitudes

        Returns:
            the probability of target index
        """
        req = qusproutdata.GetProbAmpReq(self._taskid, index)
        res = self._client.getProbAmp(req)
        return res.amp

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
        req = qusproutdata.GetProbOfOutcomeReq(self._taskid, qubit, outcome)
        res = self._client.getProbOfOutcome(req)
        return res.pro_outcome

    @timefn
    def get_prob_all_outcome(self, qubits):
        """
        Get outcomeProbs with the probabilities of every outcome of the sub-register contained in qureg

        Args:
            qubits: the sub-register contained in qureg

        Returns:
            An array contains probability of target qubits
        """
        req = qusproutdata.GetProbOfAllOutcomReq(self._taskid, qubits)
        res = self._client.getProbOfAllOutcome(req)
        return res.pro_outcomes

    @timefn
    def get_all_state(self):
        """
        Get the current state vector of probability amplitudes for a set of qubits
        """
        req = qusproutdata.GetAllStateReq(self._taskid)
        res = self._client.getAllState(req)
        return res.all_state

    @timefn
    def cancel_Cmd(self):
        req = qusproutdata.CancelCmdReq(self._taskid)
        return self._client.cancelCmd(req)

    @timefn
    def apply_QFT(self, qubits):
        """
        Applies the quantum Fourier transform (QFT) to a specific subset of qubits of the register qureg

        Args:
            qubits: a list of the qubits to operate the QFT upon
        """
        req = qusproutdata.ApplyQFTReq(self._taskid, qubits)
        res = self._client.applyQFT(req)

    @timefn
    def apply_Full_QFT(self):
        """
        Applies the quantum Fourier transform (QFT) to the entirety of qureg
        """
        req = qusproutdata.ApplyFullQFTReq(self._taskid)
        res = self._client.applyFullQFT(req)

    @timefn
    def get_expec_pauli_prod(self, pauli_prod_list):
        """
        Computes the expected value of a product of Pauli operators.

        Args:
            pauli_prod_list: a list contains the indices of the target qubits,\
                the Pauli codes (0=PAULI_I, 1=PAULI_X, 2=PAULI_Y, 3=PAULI_Z) to apply to the corresponding qubits.

        Returns:
            the expected value of a product of Pauli operators.
        """
        req = qusproutdata.GetExpecPauliProdReq(self._taskid, pauli_prod_list)
        res = self._client.getExpecPauliProd(req)
        return res.expect
    
    @timefn
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
        req = qusproutdata.GetExpecPauliSumReq(self._taskid, oper_type_list, term_coeff_list)
        res = self._client.getExpecPauliSum(req)
        return res.expect
        