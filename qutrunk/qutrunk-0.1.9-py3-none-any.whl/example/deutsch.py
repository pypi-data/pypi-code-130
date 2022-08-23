"""Example of a simple quantum random number generator."""

# https://blog.csdn.net/longji/article/details/85547108?ops_request_misc=%257B%2522request%255Fid%2522%253A%2522164756639816780261973236%2522%252C%2522scm%2522%253A%252220140713.130102334..%2522%257D&request_id=164756639816780261973236&biz_id=0&utm_medium=distribute.pc_search_result.none-task-blog-2~all~sobaiduend~default-1-85547108.142^v2^pc_search_insert_es_download,143^v4^control&utm_term=projectq&spm=1018.2226.3001.4187

from qutrunk.backends import BackendQuSprout
from qutrunk.circuit import QCircuit
from qutrunk.circuit.gates import H, Measure, All, X, CNOT


def Deutsch(backend=None):
    # allocate
    qc = QCircuit(backend=backend)
    qureg = qc.allocate(2)
    X * qureg[1]
    All(H) * qureg
    CNOT * (qureg[0], qureg[1])
    H * qureg[0]
    All(Measure) * qureg
    qc.print()
    result = qc.run()
    # TODO:??
    print("执行Deutsch算法，测量得到的结果是：", result.get_measure()[0])
    return qc


if __name__ == "__main__":
    # local run
    circuit = Deutsch()

    # qusprout run
    # circuit = Deutsch(backend=BackendQuSprout())
    print(circuit.draw())
