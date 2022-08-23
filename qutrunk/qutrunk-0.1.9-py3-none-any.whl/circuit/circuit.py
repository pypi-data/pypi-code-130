"""Circuit Module"""
import json
import random
import sys
from enum import Enum
from typing import List, Optional

from qutrunk.backends import Backend, BackendLocal
from qutrunk.circuit import CBit, CReg, QuBit, Qureg, Counter
from qutrunk.circuit.gates import MeasureGate
from qutrunk.circuit.ops import Observable


class InitState(Enum):
    """Init state for quantum circuit(represent by qureg).

    Attributes:
        Zero: Initialise qureg into the zero state
        Plus: Initialise qureg into the plus state.
        Classical: Initialise qureg into the classical state with index stateInd
    """

    ZERO = 1
    PLUS = 2
    CLASSICAL = 3


class QCircuit:
    """
    Quantum circuit

    Attributes:
        backend: Used to run quantum circuits
        density: Creates a density matrix Qureg object representing a set of \
            qubits which can enter noisy and mixed states
        name: The circuit name
        counter: Statistics the resources of circuit used
    """

    prefix = "circuit"

    def __init__(
            self,
            backend=None,
            density=False,
            name: Optional[str] = None,
            resource: Optional[bool] = False,
    ):
        self.qreg = None
        self.creg = None
        self.cmds = []
        self.init_state = None
        self.init_value = None
        self.cmd_cursor = 0
        self.counter = None

        self.qubit_indices = {}
        self.cbit_indices = {}

        # 默认使用local作为后端
        if backend is None:
            self.backend = BackendLocal()
        else:
            if not isinstance(backend, Backend):
                raise TypeError("You supplied a backend which is not supported.\n")
            self.backend = backend

        # 本地模式暂不支持噪声模型
        if density and isinstance(backend, BackendLocal):
            raise TypeError("You supplied a backend which is not supported density.\n")
        self.density = density

        self.backend.circuit = self
        self.outcome = None

        if name is None:
            name = self._generate_circuit_name()
        self.name = name

        if resource:
            self.counter = Counter(self)

    def __iter__(self):
        """
        Used to iterate commands in quantum circuits.
        """
        return QCircuitIter(self.cmds)

    def allocate(self, qubits, init_state=InitState.ZERO, init_value=0):
        """
        Allocate qubit in quantum circuit.

        Args:
            qubits: number of qubit allocated in circuit.
            init_state: Zero, Plus or Classical state.
            init_value: set the initial value if init_state == Classical

        Returns:
            qreg: the register of quantum.
        """
        self.init_state = init_state
        self.init_value = init_value
        self.qreg = Qureg(circuit=self, size=qubits)
        self.creg = CReg(circuit=self, size=qubits)

        if self.counter:
            self.counter.qubits = qubits

        for index in range(qubits):
            # 建立映射关系
            self.qubit_indices[QuBit(self.qreg, index)] = index
            self.cbit_indices[CBit(self.creg, index)] = index

        return self.qreg

    def get_init_qasm(self):
        """Convert the initialization state of the circuit into qasm instruction."""
        qasm = ""
        if self.init_state == InitState.PLUS:
            qasm += "reset q;\n"
            qasm += "h q;\n"
        elif self.init_state == InitState.CLASSICAL:
            binstr = bin(self.init_value)[2:]
            binarr = [int(b) for b in binstr]
            binarr = binarr[::-1]
            qasm += "reset q;\n"

            for i, val in enumerate(binarr):
                if val == 1:
                    qasm += "x q[" + str(i) + "];\n"
        return qasm

    def set_cmds(self, cmds):
        """
        Set cmds to circuit

        Args:
            cmds: the commands set to circuit
        """
        self.cmds = cmds

    def append_cmd(self, cmd):
        """
        Append command to circuit when apply a quantum gate

        Args:
            cmd: the command append to circuit
        """
        self.cmds.append(cmd)

    @property
    def initstate(self):
        """
        Get circuit init state
        """
        return self.init_state.value

    @property
    def initvalue(self):
        """
        Get circuit init value
        """
        return self.init_value

    def get_density(self):
        """
        Get circuit density
        """
        return self.density

    def forward(self, num):
        """
        Update the cmd_cursor when a bunch of quantum operations have been run.

        Args:
            num: the number of cmds in current bunch
        """
        self.cmd_cursor += num

    @property
    def qubits_len(self):
        """
        Get the number of qubits.
        """
        return len(self.qreg)

    @property
    def gates_len(self):
        """
        Get the number of gates
        """
        return len(self.cmds)

    def set_measure(self, qubit, value):
        """
        Store the measure result for target qubit.

        Args:
            qubit: the index of qubit in qureg
            value: the qubit measure value(0 or 1)
        """
        if qubit >= len(self.qreg) or qubit < 0:
            raise Exception("量子比特下标越界")
        self.creg[qubit].set_value(value)

    def run(self, shots=1):
        """
        Run quantum circuit through the specified backend and shots

        Args:
            shots: run times of the circuit, default: 1

        Returns:
            result: the Result object contain circuit running outcome
        """
        self.backend.send_circuit(self, True)
        result = self.backend.run(shots)
        if result and result.measureSet:
            for m in result.measureSet:
                self.set_measure(m.id, m.value)

        res = Result(self.qubits_len, result)

        return res

    def apply_QFT(self, qubits):
        """
        Applies the quantum Fourier transform (QFT) to a specific subset of qubits of the register qureg

        Args:
            qubits: a list of the qubits to operate the QFT upon
        """
        self.backend.send_circuit(self)
        self.backend.apply_QFT(qubits)

    def apply_Full_QFT(self):
        """
        Applies the quantum Fourier transform (QFT) to the entirety of qureg
        """
        self.backend.send_circuit(self)
        self.backend.apply_Full_QFT()

    def draw(self, output=None, line_length=None):
        """
        Draw quantum circuit

        Args:
            output: set the draw device
            line_length: max length to draw quantum circuit, the excess circuit will be truncated
        """
        if output is None:
            output = "text"
        # pylint: disable=C0415
        from qutrunk.visualizations import circuit_drawer

        return circuit_drawer(circuit=self, output=output, line_length=line_length)

    def __str__(self) -> str:
        return str(self.draw(output="text"))

    @property
    def qubits(self) -> List[QuBit]:
        """
        Returns a list of quantum bits
        """
        return self.qreg.qubits

    @property
    def cbits(self) -> List[CBit]:
        """
        Returns a list of cbit
        """
        return self.creg.cbits

    def _generate_circuit_name(self):
        """Generate circuit name"""
        return f"{self.prefix}-{str(random.getrandbits(15))}"

    def __len__(self) -> int:
        """Return number of operations in circuit."""
        return len(self.cmds)

    def get_prob_amp(self, index):
        """
        Get the probability of a state-vector at an index in the full state vector.

        Args:
            index: index in state vector of probability amplitudes

        Returns:
            the probability of target index
        """
        self.backend.send_circuit(self)
        prob = self.backend.get_prob_amp(index)
        return prob

    def get_prob_outcome(self, qubit, outcome):
        """
        Get the probability of a specified qubit being measured in the given outcome (0 or 1)

        Args:
            qubit: the specified qubit to be measured
            outcome: the qubit measure result(0 or 1)

        Returns:
            the probability of target qubit
        """
        self.backend.send_circuit(self)
        prob = self.backend.get_prob_outcome(qubit, outcome)
        return prob

    def get_prob_all_outcome(self, qubits):
        """
        Get outcomeProbs with the probabilities of every outcome of the sub-register contained in qureg

        Args:
            qubits: the sub-register contained in qureg

        Returns:
            An array contains probability of target qubits
        """
        self.backend.send_circuit(self)
        probs = self.backend.get_prob_all_outcome(qubits)
        return probs

    def get_all_state(self):
        """
        Get the current state vector of probability amplitudes for a set of qubits
        """
        self.backend.send_circuit(self)
        state = self.backend.get_all_state()
        return state

    def find_bit(self, bit):
        """Find locations in the circuit.

        Args:
            bit: QuBit or Cbit

        Returns:
            index
        """
        try:
            if isinstance(bit, QuBit):
                return self.qubit_indices[bit]
            elif isinstance(bit, CBit):
                return self.cbit_indices[bit]
            else:
                raise Exception(f"Could not locate bit of unknow type:{type(bit)}")
        except KeyError:
            raise Exception(f"Could not locate provided bit:{bit}")

    def inverse(self):
        """
        Invert this circuit.

        Returns:
            QCircuit: the inverted circuit.
            qreg: the  register of quntum.

        Raises:
            Error: if the circuit cannot be inverted.
        """
        inverse_circuit = QCircuit(backend=self.backend, name=self.name + "_dg")
        inverse_circuit.allocate(qubits=self.qubits_len, init_state=self.init_state, init_value=self.init_value)

        # 反转操作指令，并取门的逆
        cmds = self.cmds
        for cmd in reversed(cmds):
            if isinstance(cmd.gate, MeasureGate):
                raise ValueError("the circuit cannot be inverted.")
            cmd.inverse = True
            inverse_circuit.append_cmd(cmd)

        return inverse_circuit, inverse_circuit.qreg

    @staticmethod
    def from_qasm_file(file):
        """Take in a QASM file and generate a QCircuit object.

        Args:
            file (str): Path to the file for a QASM program
        Return:
            QCircuit: The QCircuit object for the input QASM
        """
        # pylint: disable=C0415，E0611，E1102
        from qutrunk.qasm import Qasm
        from qutrunk.converters import dag_to_circuit
        from qutrunk.converters import ast_to_dag

        qasm = Qasm(file)
        ast = qasm.parse()
        dag = ast_to_dag(ast)
        return dag_to_circuit(dag)

    def expval(self, pauli_prod: Observable):
        """
        Computes the expected value of a product of Pauli operators.

        Args:
            pauliprodlist:
                oper_type (int): Pauli operators
                target (int): indices of the target qubits
        """
        self.backend.send_circuit(self)
        expect = self.backend.get_expec_pauli_prod(pauli_prod.obs_data())
        return expect

    def expval_sum(self, pauli_coeffi: Observable, qubitnum=0):
        """
        Computes the expected value of a sum of products of Pauli operators.

        Args:
            pauliprodlist:
                oper_type (int): Pauli operators
                term_coeff (float): The coefficients of each term in the sum of Pauli products
        """
        self.backend.send_circuit(self)
        pauli_type_list, coeffi_list = pauli_coeffi.obs_data()
        if qubitnum != 0:
            if len(coeffi_list) * qubitnum != len(pauli_type_list):
                raise AttributeError("参数错误：参数数量数量的不对")
        expect = self.backend.get_expec_pauli_sum(pauli_type_list, coeffi_list)
        return expect

    def print(self):
        """
        Print quantum circuit in qutrunk form
        """
        print(f"qreg q[{str(len(self.qreg))}]")
        print(f"creg c[{str(len(self.qreg))}]")
        # todo: 增加量子线路初始化转汇编指令处理
        for c in self:
            print(c.quqasm())

    def print_qasm(self, file=None):
        """
        Convert circuit to QASM 2.0, and dump to file/stdout.
        todo: custom gate implemented by qutrunk can't be parsed by third party.
        refer to qulib1.inc and mapping.qutrunk_standard_gate.

        Args:
            file: dump the qasm to file
        """
        f = open(file, "w") if file else sys.stdout

        f.write("OPENQASM 2.0;\n")
        f.write('include "qulib1.inc";\n')
        f.write(f"qreg q[{str(len(self.qreg))}];\n")
        f.write(f"creg c[{str(len(self.qreg))}];\n")
        f.write(self.get_init_qasm())
        for c in self:
            f.write(c.qasm() + ";\n")

        if f is not sys.stdout:
            f.close()

    def show_resource(self):
        """Show resource of the circuit use"""
        if self.counter:
            self.counter.show_verbose()


class QCircuitIter:
    """The iterator for circuit"""

    def __init__(self, cmds):
        self.idx = 0
        self.cmds = cmds

    def __iter__(self):
        return self

    def __next__(self):
        if self.idx < len(self.cmds):
            idx = self.idx
            self.idx += 1
            return self.cmds[idx]
        else:
            raise StopIteration


class Result:
    """Save the result of quantum circuit running"""
    def __init__(self, num_qubits, res):
        self.states = []
        self.values = []
        # 每个量子比特的测量结果
        self.measure_result = [-1] * num_qubits
        if res and res.measureSet:
            for m in res.measureSet:
                self.set_measure(m.id, m.value)

        # 统计所有量子比特组成的比特位字符串出现的次数
        # self.outcome = res.outcomeSet
        if res and res.outcomeSet:
            self.outcome = res.outcomeSet
            for out in self.outcome:
                # 二进制字符串转换成十进制数
                if out.bitstr:
                    self.states.append(int(out.bitstr, base=2))
                    self.values.append(out.count)
        else:
            self.outcome = None

    def set_measure(self, qubit, value):
        """
        Update qubit measure value

        Args:
            qubit: the index of qubit in qureg
            value: the qubit measure value(0 or 1)
        """
        if qubit >= len(self.measure_result) or qubit < 0:
            raise Exception("量子比特下标越界")
        self.measure_result[qubit] = value

    def get_measure(self):
        """Get the measure result"""
        return self.measure_result

    def get_outcome(self):
        """Get the measure result in binary format"""
        out = self.measure_result[::-1]
        bitstr = "0b"
        for o in out:
            bitstr += str(o)
        return bitstr

    def get_counts(self):
        """Get the number of times the measurement results appear"""
        if self.outcome is None:
            return

        res = []
        for out in self.outcome:
            temp = {out.bitstr: out.count}
            res.append(temp)
        return json.dumps(res)
