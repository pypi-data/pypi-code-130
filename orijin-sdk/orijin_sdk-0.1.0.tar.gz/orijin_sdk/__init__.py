from .defaults import ENDPOINTS
from .auth import login                             # Connection Manager
from .gql import useQueryAsOn, useMutationAsOn      # Connection Manager

#region: Connection Manager

class Connection:
    domain: str
    token: str | None
    endpoints = ENDPOINTS

    def __init__(
        self, 
        domain: str = "https://staging.orijinplusserver.com", 
        token: str = "", 
        endpoints = ENDPOINTS
    ):
        """Default values are hard-coded, not taken from the environment!"""
        self.domain = domain
        self.token = token
        self.endpoints = endpoints
    
    def __init__(
        self, 
        domain: str = "https://staging.orijinplusserver.com", 
        token: str | None = None, 
        gql_endpoint: str          = "/api/gql/query",
        file_upload_endpoint: str    = "/api/gql/query",
        consumer_login_endpoint: str = "/api/auth/customer/login",
        brand_login_endpoint: str    = "/api/auth/login"
    ) -> None:
        self.domain = domain.strip('/')
        self.token = token
        self.endpoints = ENDPOINTS
        self.endpoints.gql = gql_endpoint
        self.endpoints.file_uploads = file_upload_endpoint
        self.endpoints.consumer_login = consumer_login_endpoint
        self.endpoints.brand_login = brand_login_endpoint
    
    def brand_login(self, username: str, password: str) -> None:
        self.token = login(username, password, self.domain + self.endpoints.brand_login)
    
    def consumer_login(self, username: str, password: str) -> None:
        self.token = login(username, password, self.domain + self.endpoints.consumer_login)
    
    def login(self, username: str, password: str):
        """Default login is assumed to be brand platform."""
        self.brand_login(username, password)
    
    def useQuery(self, query: str, variables):
        return useQueryAsOn(query, variables, self.token, self.domain + self.endpoints.gql)

    def useMutation(self, mutation: str, input):
        return useMutationAsOn(mutation, input, self.token, self.domain + self.endpoints.gql)

#endregion

