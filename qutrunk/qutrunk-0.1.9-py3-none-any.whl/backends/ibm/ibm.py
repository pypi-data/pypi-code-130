"""IBM Backend"""

import math

from qutrunk.backends import Backend
from qutrunk.circuit.gates import (
    Measure,
    CNOT,
    H,
    Rx,
    Ry,
    Rz,
)
from .ibm_client import send


# TODO:The IBM quantum chip can only do U1,U2,U3,barriers, and CX / CNOT.
class BackendIBM(Backend):
    """
    The BackendIBM class, which stores the circuit, transforms it to JSON,
    and sends the circuit through the IBM API.
    """
    def __init__(self, token=None, device=None):
        super().__init__()
        # 量子线路
        self.circuit = None
        # token
        self._token = token
        # 默认使用的后端 TODO:后期可选
        self.device = "ibmq_qasm_simulator"
        # 需要分配的量子比特数
        self._allocated_qubits = set()
        # 量子线路的json格式
        self._json = []
        # 测量的id
        self._measured_ids = []

    def send_circuit(self, circuit, final=False):
        """
        Send the quantum circuit to IBM backend

        Args:
            circuit: quantum circuit to send
            final: True if quantum circuit finish, default False
        """
        # 参数：量子比特数
        self._allocated_qubits.add(len(circuit.qreg))

        # 1 遍历circuit
        for ct in circuit:
            self.circuit_to_json(ct)

        # 参数：测量
        for measured_id in self._measured_ids:
            self._json.append({'qubits': [measured_id], 'name': 'measure', 'memory': [measured_id]})
        print("result==", self._json)

        # 2 组装参数
        info = {}
        # 指令集
        info['json'] = self._json

        # 量子比特数
        info["nq"] = len(circuit.qreg)
        # 计算次数
        info['shots'] = 1024
        info['maxCredits'] = 10
        info['backend'] = {'name': self.device}

        # 发送给IBM QE
        result = send(
            info,
            device=self.device,
            token=self._token,
            num_retries=1024,
            verbose=True,
        )
        print("result=", result)
        return result

    def circuit_to_json(self, cmd):
        """Translates the command and in a local variable"""
        gate = cmd.gate

        if gate is Measure:
            self._measured_ids += cmd.targets
        elif gate is CNOT and len(cmd.controls) == 1:
            self._json.append({"qubits": [*cmd.controls, *cmd.targets], "name": "cx"})
        elif gate is H:
            self._json.append({'qubits': cmd.targets, 'name': 'u2', 'params': [0, 3.141592653589793]})
        elif isinstance(gate, (Rx, Ry, Rz)):
            u_name = {'Rx': 'u3', 'Ry': 'u3', 'Rz': 'u1'}
            u_angle = {
                'Rx': [gate.angle, -math.pi / 2, math.pi / 2],
                'Ry': [gate.angle, 0, 0],
                'Rz': [gate.angle],
            }

            # 取出门对应的名称
            gate_name = u_name[str(gate)[0:2]]
            # 取出门对应的角度
            params = u_angle[str(gate)[0:2]]

            self._json.append({'qubits': cmd.targets, 'name': gate_name, 'params': params})

        else:
            raise Exception(
                'This command is not currently supported.\n'
                + 'The IBM quantum chip can only do U1,U2,U3,barriers, and CX / CNOT.'
            )

    def run(self, shots=1):
        pass