"""
Quantum Fourier Transform examples.
"""
import numpy as np

from qutrunk.circuit import QCircuit
from qutrunk.circuit.gates import H, All, P


def run_QFT():
    circuit = QCircuit()
    qureg = circuit.allocate(3)

    All(H) * qureg
    circuit.apply_QFT([q.index for q in qureg])
    print(circuit.get_all_state())

    circuit.run()


def run_Full_QFT():
    circuit = QCircuit()
    qureg = circuit.allocate(3)

    All(H) * qureg
    circuit.apply_Full_QFT()
    print(circuit.get_all_state())

    circuit.run()


def qft_single_wave():
    num_qubits = 4
    circuit = QCircuit()
    qreg = circuit.allocate(num_qubits)
    All(H) * qreg
    P(np.pi / 4) * qreg[0]
    P(np.pi / 2) * qreg[1]
    P(np.pi) | qreg[2]
    circuit.apply_Full_QFT()
    print(circuit.get_all_state())
    circuit.run()

    return circuit


if __name__ == "__main__":
    # run_QFT()
    # run_Full_QFT()
    circuit = qft_single_wave()
    print(circuit.draw())
