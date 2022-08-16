from qiskit import IBMQ, transpile, Aer
from ..utilities import JobStatus, JobResponse
import time

class QiskitFaaS:
    
    def __init__(self, backendData):
        self.token = backendData["providerToken"]
        self.hub = backendData["backendInfo"].get("hub")
        self.provider = backendData.get("provider")
        self.backendName = backendData["name"]
        self.backend = self.get_qiskit_backend()
    
    def init_ibmq_provider(self, token, hub):
        if IBMQ.active_account():
            if IBMQ.active_account()["token"] == token:
                provider = IBMQ.get_provider(hub=hub)
            else:
                IBMQ.disable_account()
                provider = IBMQ.enable_account(token, hub=hub)
        else:    
            provider = IBMQ.enable_account(token, hub=hub)
        return provider
    
    def get_qiskit_backend(self):
        if self.provider == "ibmq":
            ibmq = self.init_ibmq_provider(self.token, self.hub)
            backend = ibmq.get_backend(self.backendName)
        elif self.provider == "qfaas":
            backend = Aer.get_backend(self.backendName)
        return backend
    
    def transpile_circuit(self, qcircuit):
        transqc = transpile(qcircuit,self.backend)
        return transqc
        
    def run_job(self, qcircuit, shots):
        # Transpile circuit to adapt with backend basis gate
        qc = self.transpile_circuit(qcircuit)
        job = self.backend.run(qc, shots=shots)
        return job
    
    def submit_job(self, qcircuit, shots, interval, timeout, wait):
        if self.provider == "qfaas":
            try:
                job = self.run_job(qcircuit, shots)
                jobResult = dict(job.result().get_counts())
                jobStatus = JobStatus(
                    "DONE", "Job is successfully executed on Local Simulator"
                )
            except Exception as e:
                jobResult = {}
                jobStatus = JobStatus("ERROR", str(e))
            jobResponse = JobResponse(
                providerJobId="QFaaS-Internal-Qiskit-Simulation-Job",
                jobStatus=jobStatus,
                backend={
                    "name": self.backendName,
                    "hub": "qfaas-internal",
                },
                jobResult=jobResult,
            )
        elif self.provider == "ibmq":
            job = self.run_job(qcircuit, shots)
            jobResult = {}
            # wait for result processing
            if wait:
                # Track the status of job up to timeout (60s by default)
                jobStatus = self.ibmq_job_monitor(job, interval, timeout)
            else:
                # Track the status of job up to 10 seconds
                jobStatus = self.ibmq_job_monitor(job, 2, 5)

            if jobStatus.status == "DONE":
                counts = job.result()
                jobResult = dict(counts.get_counts())

            jobResponse = JobResponse(
                providerJobId=job.job_id(),
                jobStatus=jobStatus,
                backend={
                    "name": job.backend().name(),
                    "hub": job.backend().hub,
                },
                jobResult=jobResult,
            )
        return jobResponse
            
            
    
    def ibmq_job_monitor(self, job, interval : int, timeout: int):
        """Monitor job status at IBM Quantum

        Args:
        - job (IBMQJob): Job instance
        - interval (int): Interval time to check job status (in seconds)

        Returns:
        - Job status
        """
        status = job.status()
        proccessingTime = 0
        
        while status.name not in ["DONE", "CANCELLED", "ERROR"]:
            time.sleep(interval)
            status = job.status()
            msg = status.value
            if status.name == "QUEUED":
                details = msg + " (%s)" % job.queue_position()
            proccessingTime += interval
            if proccessingTime >= timeout:
                break
        msg = status.value
        details = msg
        jobStatus = JobStatus(status.name, details)
        return jobStatus
        