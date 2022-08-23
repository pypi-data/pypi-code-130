"""circuit转DAG"""
from qutrunk.dagcircuit.dagcircuit import DAGCircuit
from qutrunk.circuit import QuBit, CBit


def circuit_to_dag(circuit):
    """Convert circuit to DAGCircuit"""
    # 创建有向无环图的对象
    dagcircuit = DAGCircuit()
    # 量子线路名称
    dagcircuit.name = circuit.name

    # 添加量子位线路  qubits是多个QuBit的列表
    dagcircuit.add_qubits(circuit.qubits)
    # 添加经典位线路  cbits是多个CBit的列表
    dagcircuit.add_cbits(circuit.cbits)

    # 添加操作节点
    for cmd in circuit.cmds:
        # 调用函数，解析每一条指令
        qargs, cargs = __operation_command(cmd, circuit)
        dagcircuit.apply_operation_back(cmd, qargs, cargs)

    return dagcircuit


def __operation_command(command, circuit):
    """Rebuild instruction"""
    qargs = []
    cargs = []

    for c in command.controls:
        qubit = QuBit(circuit.qreg, index=c)
        qargs.append(qubit)

    for c in command.targets:
        qubit = QuBit(circuit.qreg, index=c)
        qargs.append(qubit)

    if str(command.gate) == "Measure":
        cbit = CBit(circuit.creg, index=command.targets[0])
        cargs.append(cbit)

    return qargs, cargs
