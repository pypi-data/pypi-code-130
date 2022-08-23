from numpy import pi

from qutrunk.circuit import QCircuit
from qutrunk.circuit.gates import (
    H, Measure, CNOT, Toffoli, P, R, Rx, Ry, Rz, S, Sdg, T, Tdg, X, Y, Z, MCX, MCZ,
    NOT, Swap, SqrtSwap, SqrtX, All, CP, CY, CZ, CRx, CRy, CRz, Rxx, Ryy, Rzz,
    U1, U2, U3, Barrier, CR, CU, CU1, CU3, CX, iSwap, Y1, X1
)


def run_gates():
    # allocate
    qc = QCircuit()
    qr = qc.allocate(3)

    # apply gate
    H * qr[0]
    CNOT * (qr[0], qr[1])
    NOT * qr[0]
    Toffoli * (qr[0], qr[1], qr[2])
    P(pi / 2) * qr[2]
    R(pi / 2, pi / 2) * qr[0]
    Rx(pi / 2) * qr[1]
    Ry(pi / 2) * qr[1]
    Rz(pi / 2) * qr[1]
    S * qr[0]
    Sdg * qr[0]
    T * qr[0]
    Tdg * qr[0]
    X * qr[2]
    Y * qr[2]
    Z * qr[2]
    X1 * qr[0]
    Y1 * qr[0]
    # Z1 * qr[0]
    Swap * (qr[0], qr[1])
    iSwap(pi / 2) * (qr[0], qr[1])
    SqrtSwap * (qr[0], qr[1])  # 未定义符合
    SqrtX * qr[0]

    CX * (qr[0], qr[1])
    CY * (qr[0], qr[1])
    CZ * (qr[0], qr[1])
    CP(pi / 2) * (qr[0], qr[1])  # 未定义符合
    CR(pi / 2) * (qr[0], qr[1])
    CRx(pi / 2) * (qr[0], qr[1])
    CRy(pi / 2) * (qr[0], qr[1])
    CRz(pi / 2) * (qr[0], qr[1])
    MCX(2) * (qr[0], qr[1], qr[2])
    MCZ(2) * (qr[0], qr[1], qr[2])

    Rxx(pi / 2) * (qr[0], qr[1])
    Ryy(pi / 2) * (qr[0], qr[1])
    Rzz(pi / 2) * (qr[0], qr[1])

    U1(pi / 2) * qr[0]
    U2(pi / 2, pi / 2) * qr[0]
    U3(pi / 2, pi / 2, pi / 2) * qr[0]
    CU(pi / 2, pi / 2, pi / 2, pi / 2) * (qr[0], qr[1])
    CU1(pi / 2) * (qr[1], qr[2])
    CU3(pi / 2, pi / 2, pi / 2) * (qr[0], qr[1])

    Barrier * qr

    All(Measure) * qr

    # print circuit
    qc.print()
    qc.print_qasm()

    qc.run()

    return qc


if __name__ == '__main__':
    circuit = run_gates()
    print(circuit.draw(line_length=3000))
    circuit.print_qasm("allgates-temp.qasm")
