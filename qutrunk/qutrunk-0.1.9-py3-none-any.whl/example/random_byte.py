from qutrunk.circuit import QCircuit, Counter
from qutrunk.circuit.gates import H, Measure, All
from qutrunk.backends import BackendQuSprout


def run_random_byte(backend=None):
    # allocate
    qc = QCircuit(backend)

    qureg = qc.allocate(8)
    # 将统计信息归集到Counter类
    ct = Counter(qc)

    All(H) * qureg
    All(Measure) * qureg

    # print circuit
    qc.print()

    # run circuit
    res = qc.run()

    # print([int(q) for q in qureg])
    print(res.get_measure())
    ct.show_verbose()
    return qc


if __name__ == "__main__":
    # local run
    circuit = run_random_byte()

    # qusprout run
    # circuit = run_random_byte(backend=BackendQuSprout())

    # qusprout mpi run
    # circuit = run_random_byte(backend=BackendQuSprout(ExecType.Mpi))

    print(circuit.draw())
