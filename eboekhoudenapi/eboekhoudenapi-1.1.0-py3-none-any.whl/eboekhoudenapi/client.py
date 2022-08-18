from zeep import Client as ZeepClient
from .models import Mutatie


class Client:
    client = None
    session_id: str = None

    username: str = None
    security_code_1: str = None
    security_code_2: str = None

    def __init__(self, username: str, security_code_1: str, security_code_2: str):
        self.username = username
        self.security_code_1 = security_code_1
        self.security_code_2 = security_code_2
        self.client = ZeepClient("https://soap.e-boekhouden.nl/soap.asmx?wsdl")
        self.connect()

    def connect(self):
        session = self.client.service.OpenSession(
            Username=self.username, SecurityCode1=self.security_code_1, SecurityCode2=self.security_code_2
        )
        self.session_id = session["SessionID"]

    def add_mutatie(self, mutatie: Mutatie):
        exported_mutatie = mutatie.export()
        params = dict(SessionID=self.session_id, SecurityCode2=self.security_code_2, oMut=exported_mutatie)
        response = self.client.service.AddMutatie(**params)
        return response
