"""
将量子线路表示为有向无环图（DAG)
"""
from collections import OrderedDict

import retworkx as rx
import itertools

from .dagnode import DAGInNode, DAGOutNode, DAGOpNode
from qutrunk.circuit import QuBit, CBit, Qureg, CReg


class DAGCircuit:
    """
    Convert quantum circuit to a directed acyclic graph(DAG)
    """

    def __init__(self):
        """Create an empty circuit."""
        # 量子电路图名称
        self.name = None
        # 量子电路元信息
        self.metadata = None
        # 线，元素是QuBit或CBit对象
        self._wires = set()
        # 输入节点
        self.input_map = OrderedDict()
        # 输出节点
        self.output_map = OrderedDict()
        # 创建一个空无向图
        self._multi_graph = rx.PyDAG()
        # 量子比特
        self.qubits = []
        # 经典比特
        self.cbits = []
        # 操作指令
        self._op_names = {}

        # Map of qreg/creg name to Register object.
        self.qregs = OrderedDict()
        self.cregs = OrderedDict()

    def _add_wire(self, wire):
        """
        Add a qubit or cbit to the circuit.

        Args:
            wire: the object of qubit or cbit
        """

        if wire not in self._wires:
            self._wires.add(wire)

            # 输入结点
            input_node = DAGInNode(wire=wire)
            # 输出结点
            output_node = DAGOutNode(wire=wire)
            # 添加一个新node到图中，返回结点的index
            input_map_id, output_map_id = self._multi_graph.add_nodes_from([input_node, output_node])
            input_node._node_id = input_map_id
            output_node._node_id = output_map_id

            self.input_map[wire] = input_node
            self.output_map[wire] = output_node
            # 在input_node结点和output_node结点之间添加一条边，边的数据是wire，即qubit对象或cbit对象
            self._multi_graph.add_edge(input_node._node_id, output_node._node_id, wire)
        else:
            raise ValueError(f"duplicate wire {wire}")

    def add_qubits(self, qubits):
        """
        Add qubits to DAGCircuit, and add wires
        """
        if any(not isinstance(qubit, QuBit) for qubit in qubits):
            raise ValueError("not a QuBit instance.")

        duplicate_qubits = set(self.qubits).intersection(qubits)
        if duplicate_qubits:
            raise ValueError(f"duplicate qubits {duplicate_qubits}")

        self.qubits.extend(qubits)
        for qubit in qubits:
            self._add_wire(qubit)

    def add_cbits(self, cbits):
        """Add classical bits to DAGCircuit, and add wires"""
        if any(not isinstance(cbit, CBit) for cbit in cbits):
            raise ValueError("not a CBit instance.")

        duplicate_cbits = set(self.cbits).intersection(cbits)
        if duplicate_cbits:
            raise ValueError(f"duplicate cbits {duplicate_cbits}")

        self.cbits.extend(cbits)
        for cbit in cbits:
            self._add_wire(cbit)

    def topological_nodes(self, key=None):
        """Return nodes in topological sort order"""
        def _key(x):
            return x.sort_key

        if key is None:
            key = _key

        return iter(rx.lexicographical_topological_sort(self._multi_graph, key=key))

    def topological_op_nodes(self, key=None):
        """Return op nodes in topological sort order"""
        return (nd for nd in self.topological_nodes(key) if isinstance(nd, DAGOpNode))

    @property
    def wires(self):
        """Return a list of the wires in order."""
        return self.qubits + self.cbits

    def _add_op_node(self, op, qargs, cargs):
        """
        Add operation node

        Args:
            op: the operation associated with DAG node.
            qargs: a list of QuBit.
            cargs: a list of CBit.

        Returns:
            node_index: The integer node index for the new opetation node on the DAG.
        """
        new_node = DAGOpNode(op=op, qargs=qargs, cargs=cargs)

        node_index = self._multi_graph.add_node(new_node)
        new_node._node_id = node_index
        self._increment_op(op)

        return node_index

    def apply_operation_back(self, op, qargs=[], cargs=[]):
        """
        Add operation node at the end of DAG

        Args:
            op (Commands): the operation associated with the DAG node
            qargs (list[QuBit]): qubits that op will be applied to
            cargs (list[CBit]): cbits that op will be applied to
        """
        # 添加节点
        node_index = self._add_op_node(op, qargs, cargs)

        all_bit = [qargs, cargs]
        self._multi_graph.insert_node_on_in_edges_multiple(
            node_index, [self.output_map[q]._node_id for q in itertools.chain(*all_bit)]
        )
        return self._multi_graph[node_index]

    def add_qreg(self, qreg):
        """Add all wires in a quantum register."""
        # 判断qreg是否是量子寄存器类型？
        if not isinstance(qreg, Qureg):
            raise ValueError("not a Qureg instance.")

        if qreg.name in self.qregs:
            raise ValueError(f"duplicate register {qreg.name}")

        self.qregs[qreg.name] = qreg
        existing_qubits = set(self.qubits)
        for j in range(qreg.size):
            if qreg[j] not in existing_qubits:
                self.qubits.append(qreg[j])
                self._add_wire(qreg[j])

    def add_creg(self, creg):
        """Add all wires in a classical register."""
        if not isinstance(creg, CReg):
            raise ValueError("not a CReg instance.")
        if creg.name in self.cregs:
            raise ValueError(f"duplicate register {creg.name}")
        self.cregs[creg.name] = creg
        existing_cbits = set(self.cbits)
        for j in range(creg.size):
            if creg[j] not in existing_cbits:
                self.cbits.append(creg[j])
                self._add_wire(creg[j])

    def _increment_op(self, op):
        """Count the number of each door operation"""
        if op.name in self._op_names:
            self._op_names[op.name] += 1
        else:
            self._op_names[op.name] = 1

