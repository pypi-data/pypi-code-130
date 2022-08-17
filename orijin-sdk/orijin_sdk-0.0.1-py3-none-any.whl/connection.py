from . import types, gql_helpers
from .auth import login
from .gql import useQueryAsOn, useMutationAsOn

class connection:
    domain: str
    token: str | None
    endpoints: types.endpoints

    def __init__(
        self, 
        domain: str = "https://staging.orijinplusserver.com", 
        token: str = "", 
        endpoints: types.endpoints = types.endpoints()
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
        """Default values are hard-coded, not taken from the environment!"""
        self.domain = domain
        self.token = token
        self.endpoints = types.endpoints()
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
        return self.brand_login(username, password)
    
    def useQuery(self, query: str, input):
        return useQueryAsOn(query, input, self.token, self.domain + self.endpoints.gql)

    def useMutation(self, mutation: str, input):
        return useMutationAsOn(mutation, input, self.token, self.domain + self.endpoints.gql)

    # Helper functions.
    
    def upload_sku(self, sku: types.UpdateSku):
        """Use GQL mutation.skuCreate
        
        Args:
            sku: (UpdateSku): The sku data to be uploaded
        
        Returns:
            New id of sku just uploaded.
        """
        return gql_helpers.upload_sku(sku, self.token, self.domain + self.endpoints.gql)
    
    def upload_order(self, order: types.UpdateOrder):
        """Use GQL mutation.___Create
        
        Args:
            ___: (___): The ___ data to be uploaded
        
        Returns:
            New id of ___ just uploaded.
        """
        return gql_helpers.upload_order(order, self.token, self.domain + self.endpoints.gql)
    
    def upload_container(self, container: types.CreateContainer):
        """Use GQL mutation.___Create
        
        Args:
            ___: (___): The ___ data to be uploaded
        
        Returns:
            True/False of success
        """
        return gql_helpers.upload_container(container, self.token, self.domain + self.endpoints.gql)
    
    def upload_pallet(self, pallet: types.CreatePallet):
        """Use GQL mutation.___Create
        
        Args:
            ___: (___): The ___ data to be uploaded
        
        Returns:
            True/False of success
        """
        return gql_helpers.upload_pallet(pallet, self.token, self.domain + self.endpoints.gql)
    
    def upload_carton(self, carton: types.CreateCarton):
        """Use GQL mutation.___Create
        
        Args:
            ___: (___): The ___ data to be uploaded
        
        Returns:
            True/False of success
        """
        return gql_helpers.upload_carton(carton, self.token, self.domain + self.endpoints.gql)
    
    def upload_product(self, product: types.UpdateProduct):
        """Use GQL mutation.___Create
        
        Args:
            ___: (___): The ___ data to be uploaded
        
        Returns:
            New id of ___ just uploaded.
        """
        return gql_helpers.upload_product(product, self.token, self.domain + self.endpoints.gql)
