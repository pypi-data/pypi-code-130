from qutrunk.circuit import QCircuit, InitState
from qutrunk.circuit.gates import CNOT, Measure, Toffoli, X, All, MCX


def increment(num_qubits, initvalue):
    """自增运行"""
    circuit = QCircuit()
    qr = circuit.allocate(num_qubits, InitState.CLASSICAL, initvalue)

    # for i in range(num_qubits-1):
    #     ctrl_bits = qr[:num_qubits-1-i]
    #     C(NOT, num_qubits-1-i) | (*ctrl_bits, qr[num_qubits-1-i])
    # X | qr[0]

    # 等同于下面的代码
    MCX(3) * (qr[0], qr[1], qr[2], qr[3])
    Toffoli * (qr[0], qr[1], qr[2])
    CNOT * (qr[0], qr[1])
    X * qr[0]

    All(Measure) * qr
    res = circuit.run()
    print(res.get_outcome())

    return circuit


def decrement(num_qubits, initvalue):
    """自减运行"""
    circuit = QCircuit()
    qr = circuit.allocate(num_qubits, InitState.CLASSICAL, initvalue)

    # X | qr[0]
    # for i in range(num_qubits-1):
    #     ctrl_bits = qr[:1+i]
    #     C(NOT, 1+i) | (*ctrl_bits, qr[1+i])

    # 等同于下面的代码
    X * qr[0]
    CNOT * (qr[0], qr[1])
    Toffoli * (qr[0], qr[1], qr[2])
    MCX(3) * (qr[0], qr[1], qr[2], qr[3])

    All(Measure) * qr
    res = circuit.run()
    print(res.get_outcome())
    return circuit


if __name__ == "__main__":
    circuit = increment(4, 0)

    # circuit = decrement(4, 0b0001)

    print(circuit.draw())
