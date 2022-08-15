class JobStatus(object):
    def __init__(self, status="", details=""):
        self.status = status if status else "ERROR"
        self.details = (
            details
            if details
            else "Job is failed or incomplete. Please try again later."
        )


class JobResponse(object):
    def __init__(
        self,
        providerJobId: str = "",
        jobStatus: JobStatus = None,
        backend={},
        jobResult={},
    ):
        self.providerJobId = providerJobId if providerJobId else ""
        self.jobStatus = jobStatus if jobStatus else JobStatus()
        self.backend = backend if backend else {"name": "UNKNOWN"}
        self.jobResult = jobResult if jobResult else {}


class Utils:
    def __init__(self):
        pass

    def generate_response(job: JobResponse) -> dict:
        if job:
            statusCode = 201  # not yet finished
            if job.jobStatus.status == "DONE":
                statusCode = 200
            job.jobStatus = vars(job.jobStatus)
            job = vars(job)  # Object to directory
            response = {"statusCode": statusCode, "body": job}
        else:
            response = {
                "statusCode": 500,
                "body": "Error in function code. Please contact the developer.",
            }
        return response

    def generate_post_processed_response(jobResult) -> dict:
        statusCode = 200
        jobStatus = JobStatus("DONE", "Job post processing completed")
        response = {
            "statusCode": statusCode,
            "body": {"jobResult": jobResult, "jobStatus": vars(jobStatus)},
        }
        return response

    def generate_dict_output(data, details) -> dict:
        output = {"data": data, "details": details}
        return output

    def counts_post_process(job: JobResponse) -> dict:
        try:
            jobResult = job.jobResult
            if jobResult:
                result = max(jobResult, key=jobResult.get)
                occurrence = max(jobResult.values())
                allPossibleValues = {
                    k: int(k, 2) for k, v in jobResult.items() if v == occurrence
                }
                details = {
                    "decimalValue": int(result, 2),
                    "numberOfOccurence": occurrence,
                    "allPossibleValues": allPossibleValues,
                }
                job.jobResult = {"data": result, "details": details}
        except:
            job = JobResponse()
        return job
