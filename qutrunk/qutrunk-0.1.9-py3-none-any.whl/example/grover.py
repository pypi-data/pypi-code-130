"""Grover's search algorithm."""
import math
import random

from numpy import pi

from qutrunk.circuit import QCircuit, InitState
from qutrunk.circuit.gates import H, X, MCZ
from qutrunk.backends import BackendQuSprout


def apply_oracle(qr, num_qubits, sol_elem):
    for q in range(num_qubits):
        if ((sol_elem >> q) & 1) == 0:
            X * qr[q]

    ctrls = []
    for q in range(num_qubits):
        ctrls.append(qr[q])
    MCZ(len(ctrls) - 1) | (tuple(ctrls))

    for q in range(num_qubits):
        if ((sol_elem >> q) & 1) == 0:
            X * qr[q]


def apply_diffuser(qr, num_qubits):
    for q in range(num_qubits):
        H * qr[q]

    for q in range(num_qubits):
        X * qr[q]

    ctrls = []
    for q in range(num_qubits):
        ctrls.append(qr[q])
    MCZ(len(ctrls) - 1) | (tuple(ctrls))

    for q in range(num_qubits):
        X * qr[q]

    for q in range(num_qubits):
        H * qr[q]


def run_grover(qubits=15, backend=None):
    num_qubits = qubits
    num_elems = 2 ** num_qubits
    num_reps = math.ceil(pi / 4 * math.sqrt(num_elems))
    print("num_qubits:", num_qubits, "num_elems:", num_elems, "num_reps:", num_reps)

    sol_elem = random.randint(0, num_elems - 1)

    circuit = QCircuit(backend=backend, resource=True)

    qureg = circuit.allocate(num_qubits, InitState.PLUS)

    for _ in range(num_reps):
        apply_oracle(qureg, num_qubits, sol_elem)
        apply_diffuser(qureg, num_qubits)
        prob_amp = circuit.get_prob_amp(sol_elem)
        print(f"prob of solution |{sol_elem}> = {prob_amp}")

    # invert circuit
    # circuit, _ = circuit.inverse()
    # 运行线路
    circuit.run()
    # circuit.show_resource()

    return circuit


if __name__ == '__main__':
    # local run
    # circuit = run_grover()

    # qusprout run
    # circuit =run_grover(backend=BackendQuSprout())

    # qusprout mpi run
    # run_grover(backend=BackendQuSprout(ExecType.Mpi))

    # print(circuit.draw(line_length=300))

    # 性能测试
    import cProfile
    cProfile.run("run_grover()")

