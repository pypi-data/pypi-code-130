class APIs:
    """For IDE prompting (instead of entering API addresses all over the place), define what endpoints the system will use endpoints here."""
    def __init__(
        self,
        domain: str            = "",
        gql: str               = "/api/gql/query",
        file_uploads: str      = "/api/gql/query",
        consumer_login: str    = "/api/auth/customer/login",
        consumer_register: str = "/api/auth/customer/register",
        brand_login: str       = "/api/auth/login",
        brand_register: str    = "/api/auth/member/register",
    ) -> None:
        self.gql                = domain + gql
        self.file_uploads       = domain + file_uploads
        self.consumer_login     = domain + consumer_login
        self.consumer_register  = domain + consumer_register
        self.brand_login        = domain + brand_login
        self.brand_register     = domain + brand_register