from qutrunk.converters.circuit_to_dag import circuit_to_dag


def _get_instructions(circuit):
    """
    Given a circuit, return a tuple(qubits, cbits, nodes)
    Args:
        circuit: a quantum circuit.
    Returns:
        qubits: a list of QuBit.
        cbits: a list of CBit.
        nodes: nodes is a list of DAG nodes whose type is "operation".
            (qubits, cbits, nodes)
    """
    # 1 将circuit表示为DAG
    dag = circuit_to_dag(circuit)

    # 2 获取量子电路的量子比特数qubits和经典比特数cbits
    qubits = dag.qubits
    cbits = dag.cbits

    # 3 获取DAG的操作节点
    nodes = []
    # 按照有向无环图的拓扑排序顺序返回节点
    for node in dag.topological_op_nodes():
        nodes.append([node])
    nodes = [[node for node in layer if any(q in qubits for q in node.qargs)] for layer in nodes]

    return qubits, cbits, nodes
