class RequestData:
    
    def __init__(self, event, sdk: str, gateway: str = "http://qfaas-core.qfaas.svc.cluster.local/api"):
        self.data = event.json
        self.input = event.json.get("input")
        self.shots = event.json.get("shots")
        self.provider = event.json.get("provider")
        self.wait = bool(event.json.get("waitForResult"))
        self.postProcessOnly = bool(event.json.get("postProcessOnly"))
        self.headers = {"Authorization": event.headers.get("Authorization")}
        self.sdk = sdk
        self.gateway = gateway
        self.jobRawResult = ""
        if self.postProcessOnly:
            try:
                self.jobRawResult = event.json.get("jobRawResult")
            except:
                pass
    

    