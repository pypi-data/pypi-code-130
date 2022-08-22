from typing import Optional, Tuple


def get_authorization_scheme_param(authorization_header_value: str) -> Tuple[str, str]:
    if not authorization_header_value:
        return "", ""
    scheme, _, param = authorization_header_value.partition(" ")
    return scheme, param


class OAuth2PasswordBearer:
    def __init__(self, auto_error: bool = True):
        self.auto_error = auto_error

    async def __call__(self, request) -> Optional[str]:
        authorization: str = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise Exception("Could not validate credentials")
            else:
                return None
        return param
