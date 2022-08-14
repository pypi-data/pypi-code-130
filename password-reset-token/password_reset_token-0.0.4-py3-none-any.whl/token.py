from time import time
from functools import lru_cache
from dataclasses import dataclass

from .defaults import JWT_DEFAULT_ALGORITHM, JWT_DEFAULT_EXPIRATION_TIME_SECONDS

import jwt

@dataclass(frozen=True)
class PasswordResetToken:
    """Represents a pasword reset token based on JWT."""
    json_web_token: str
    secret: str
    algorithm: str = JWT_DEFAULT_ALGORITHM

    @lru_cache(maxsize=1)
    def get_payload(self) -> dict:
        """Returns the payload for this token as a dict."""
        try:
            payload = self.__decode_jwt()
        except Exception:
            payload = {}
        finally:
            return payload

    def is_expired(self) -> bool:
        """Checks if this token is expired, you should stop processing the token immediately if this method returns True."""
        try:
            self.__decode_jwt()
            return False
        except (jwt.exceptions.ExpiredSignatureError, jwt.exceptions.DecodeError):
            return True

    def get_user_identifier(self) -> int | str | None:
        """Returns user identifier (sub) from this token, this method is a shortcut for `get_payload().get('sub')`."""
        return self.get_payload().get('sub')

    def __decode_jwt(self) -> dict:
        return jwt.decode(self.json_web_token, self.secret, self.algorithm, options={
            "require": ["exp", "sub"]
        })

class PasswordResetTokenGenerator:
    """Class which generates PasswordResetToken instances for you."""
    def __init__(self, secret: str, algorithm: str = JWT_DEFAULT_ALGORITHM) -> None:
        self.secret = secret
        self.algorithm = algorithm

    def generate_new_token(self, user_identifier: int | str, additional_claims: dict = {}) -> PasswordResetToken:
        """Generates PasswordResetToken instance for you using given arguments."""
        jwt_payload = {}
        jwt_payload.update(additional_claims)

        exp = additional_claims.get('exp')

        if exp is None:
            exp = int(time()) + JWT_DEFAULT_EXPIRATION_TIME_SECONDS

        jwt_payload.update({
            "sub": user_identifier,
            "exp": exp
        })

        json_web_token = jwt.encode(jwt_payload, self.secret, self.algorithm)
        return PasswordResetToken(json_web_token, self.secret, self.algorithm)
