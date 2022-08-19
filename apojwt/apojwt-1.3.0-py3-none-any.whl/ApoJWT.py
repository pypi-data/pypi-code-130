from datetime import datetime, timezone
import jwt
from functools import wraps

class ApoJWT():
    """A standard JWT implementation that provides decorators to validate jwt claims
    
    A function to create a new JWT is also present

    secret: Secret string used to encode and decode the JWT
    iss: Issuer string used for additional security
    admin_audience: The name of the audience that has access to all endpoints. Default admin
    algorithm: The algorithm to use when encoding/decoding. Default HS256
    token_finder: Function used to retrive the JWT from the http request. Default None
    """

    def __init__(self, secret: str, iss: str="", admin_audience: str="admin", algorithm: str="HS256", token_finder=None):
        self.token_f = token_finder
        self.secret = str(secret)
        self.iss = str(iss)
        self.algo = algorithm
        self.admin_aud = admin_audience


    def token_required(self, fn):
        """Verifies a JWT and all its claims
        
        auth_header: http "Authorization" request header (contains the JWT)

        Raises an exception if any claims are invalid
            - expired token
            - invalid secret
            - invalid issuer
        """
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if self.token_f is None:
                raise TypeError("ApoJWT requires the token_finder attribute to be defined for validating JWTs")
            token = self.token_f()
            jwt.decode(token, self.secret, issuer=self.iss, algorithms=[self.algo])
            return fn(*args, **kwargs)
        return wrapper
        

    def permission_required(self, permission: str):
        """Verifies a JWT and ensures it contains the correct permission (audience) for the service
        
        auth_header: http "Authorization" request header (contains the JWT)
        permission: a permission (or aud) in the format <service>:<permission-name>:<resource-id>
            - Ex. "trial:UpdateTrial:<trial-id>"

        Raises an exception if any claims are invalid
            - expired token
            - invalid secret
            - invalid issuer
            - invalid audience (permission)
        """
        def decorated(fn):
            @wraps(fn)
            def wrapper(*args, **kwargs):
                if self.token_f is None:
                    raise TypeError("ApoJWT requires the token_finder attribute to be defined for validating JWTs")
                token = self.token_f()
                try:
                    jwt.decode(token, self.secret, issuer=self.iss, audience=permission, algorithms=[self.algo])
                except jwt.exceptions.InvalidAudienceError:
                    jwt.decode(token, self.secret, issuer=self.iss, audience=self.admin_aud, algorithms=[self.algo])
                return fn(*args, **kwargs)
            return wrapper
        return decorated


    def token_data(self):
        """Retrieves the additional data stored in the JWT payload"""
        token = self.token_f()
        data = jwt.decode(token, self.secret, issuer=self.iss, algorithms=[self.algo])["data"]
        return data


    def create_token(self, exp: int, aud: list[str]=[], data: dict=dict()):
        """Encodes a jwt token with the given secret

        exp: Expiration epoch time (as a numeric) of the token
        aud: List of permissions (audiences) to assign to the token
        data: Any additional information that is needed

        JWT will contain the following claims:
            - exp: Expiration Time
            - nbf: Not Before Time
            - iss: Issuer
            - aud: Audience
            - iat: Issued At
        """

        payload = {
            "exp": int(exp),
            "nbf": datetime.now(tz=timezone.utc),
            "iss": self.iss,
            "aud": list(aud),
            "iat": datetime.now(tz=timezone.utc),
            "data": data
        }
    
        return jwt.encode(payload, self.secret, algorithm=self.algo)
