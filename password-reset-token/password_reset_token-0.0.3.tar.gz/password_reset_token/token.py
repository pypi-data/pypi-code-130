from time import time
from dataclasses import dataclass

from .defaults import JWT_DEFAULT_ALGORITHM, JWT_DEFAULT_EXPIRATION_TIME_SECONDS

import jwt

@dataclass(frozen=True)
class PasswordResetToken:
    """Represents a pasword reset token based on JWT."""
    json_web_token: str
    secret: str
    algorithm: str = JWT_DEFAULT_ALGORITHM

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

    def __decode_jwt(self) -> dict:
        return jwt.decode(self.json_web_token, self.secret, self.algorithm, options={
            "require": ["exp"]
        })

class PasswordResetTokenGenerator:
    """Class which generates PasswordResetToken instances for you."""
    def __init__(self, secret: str, algorithm: str = JWT_DEFAULT_ALGORITHM) -> None:
        self.secret = secret
        self.algorithm = algorithm

    def generate_new_token(self, payload: dict, exp: int = 0) -> PasswordResetToken:
        """Generates PasswordResetToken instance for you using given arguments."""
        exp = int(exp)
        use_default_expiration_time = exp == 0

        if use_default_expiration_time:
            exp = int(time()) + JWT_DEFAULT_EXPIRATION_TIME_SECONDS

        payload.update({
            "exp": exp
        })

        json_web_token = jwt.encode(payload, self.secret, self.algorithm)
        return PasswordResetToken(json_web_token, self.secret, self.algorithm)
