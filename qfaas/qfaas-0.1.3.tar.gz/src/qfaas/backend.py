from enum import auto
import requests
from .dataUtils import RequestData
from .utilities import JobResponse, Utils, JobStatus


class Backend:
    def __init__(self, requestData: RequestData, circuit):
        self.sdk = requestData.sdk
        self.gateway = requestData.gateway
        self.headers = requestData.headers
        self.input = requestData.input
        self.rQubit = self.get_qubit_number(circuit)
        self.shots = requestData.shots
        self.wait = requestData.wait
        self.provider = requestData.provider
        self.backendRequest = self.generate_backend_request(requestData.data)
        # Get backend data from QFaaS Core API and generate backend instance
        self.backendData = self.get_backend_data()

    def get_qubit_number(self, circuit) -> int:
        if self.sdk == "qiskit":
            rQubit = int(circuit.num_qubits)
        elif self.sdk == "braket":
            rQubit = int(circuit.qubit_count)
        elif self.sdk == "cirq":
            rQubit = int(len(circuit.all_qubits()))
        elif self.sdk == "qsharp":
            rQubit = int(self.input)  # Temporarily
        return rQubit

    def generate_backend_request(self, jsonData):
        autoSelect = jsonData.get("autoSelect")
        backendName = "" if autoSelect else jsonData.get("backendName")
        backendType = (
            jsonData.get("backendType")
            if jsonData.get("backendType") in ["simulator", "qpu"]
            else "simulator"
        )

        backendRequest = {
            "sdk": self.sdk,
            "rQubit": self.rQubit,
            "provider": self.provider,
            "type": backendType,
            "autoSelect": autoSelect,
            "backendName": backendName,
        }

        return backendRequest

    def get_backend_data(self):
        response = requests.post(
            self.gateway + "/backend/select",
            json=self.backendRequest,
            headers=self.headers,
        )
        if response.json().get("code") == 200:
            try:
                backendData = response.json().get("data")[0]
            except:
                return None
            return backendData
        else:
            return None

    def submit_job(self, circuit, interval: int = 3, timeout: int = 30) -> JobResponse:
        jobResponse = JobResponse()
        shots = self.shots
        wait = self.wait
        if circuit and self.backendData and interval > 0 and interval <= timeout:
            if self.sdk == "qiskit":
                from .sdk.qiskit import QiskitFaaS

                beInstance = QiskitFaaS(self.backendData)
                jobResponse = beInstance.submit_job(
                    circuit, shots=shots, interval=interval, timeout=timeout, wait=wait
                )
            elif self.sdk == "braket":
                from .sdk.braket import BraketFaaS

                beInstance = BraketFaaS(self.backendData)
                jobResponse = beInstance.submit_job(circuit, shots=shots)

            elif self.sdk == "cirq":
                from .sdk.cirq import CirqFaaS

                beInstance = CirqFaaS(self.backendData)
                jobResponse = beInstance.submit_job(circuit, shots=shots)

            elif self.sdk == "qsharp":
                from .sdk.qsharp import QsharpFaaS

                beInstance = QsharpFaaS(self.backendData)
                jobResponse = beInstance.submit_job(circuit, self.input)
        elif self.backendData is None:
            jobResponse.backend = {"name": "Not found"}
            jobResponse.jobStatus.details = (
                "No backend matching the criteria. Please check your input."
            )
        return jobResponse

    def generate_job_response(self, job):
        jobResult = None
        jobStatus = self.monitor_job(job, 1, 2)
        if jobStatus.status == "DONE":
            jobResult = job.result()
        output = {
            "providerJobId": job.job_id(),
            "jobStatus": jobStatus,
            "backend": job.backend().name(),
            "jobResult": jobResult,
        }
        return output

    def get_job_results(self, job):
        if self.sdk == "qiskit":
            jobResult = job.result()
            return jobResult
