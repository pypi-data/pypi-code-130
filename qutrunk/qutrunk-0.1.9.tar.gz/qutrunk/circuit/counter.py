# TODO: 用于统计量子线路所需的资源：量子比特数，量子门数；量子线路编译耗时，运行耗时
import time


class Counter:
    """
    resources of circuit
    """
    def __init__(self, circuit):
        self.circuit = circuit
        self.qubits = 0
        self.quantum_gates = 0
        self.start_time = time.time()
        self.total_time = 0
        self.backend_time = 0
        self.qutrunk_time = 0

    def acc_run_time(self, elapsed):
        """Accumulate backend running time"""
        self.backend_time += elapsed

    def finish(self):
        """Statistics time and gates when circuit running finish"""
        self.total_time = time.time() - self.start_time
        self.qutrunk_time = self.total_time - self.backend_time
        self.quantum_gates = self.circuit.gates_len
    
    def __repr__(self):
        return f"Counter(quit={self.qubits})"

    def show_verbose(self):
        """Print the resource info of circuit"""
        print("==================Counter==================")
        print(self)
        print("qubits =", self.qubits)
        print("quantum_gates =", self.quantum_gates)
        print("total_time =", self.total_time)
        print("qutrunk_time =", self.qutrunk_time)
        print("backend_time =", self.backend_time)
