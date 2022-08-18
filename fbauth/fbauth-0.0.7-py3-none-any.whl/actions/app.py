from fastberry import Fastberry

from .. import types
from ..database import SQL

SETTINGS = Fastberry()

UserDB = SQL(types.User)
RoleDB = SQL(types.Role)


# Security Settings
SECURITY_SETTINGS = getattr(SETTINGS.base, "security", None)
MESSAGE = """\nIn "settings.yaml" add the following:
------------------------------------------
SECURITY:
    access_token_url: login
    access_token_expire_minutes: 1440
"""

if SECURITY_SETTINGS:
    ACCESS_TOKEN_URL = SETTINGS.base.security.get("access_token_url", "token")
    ACCESS_TOKEN_EXPIRE_MINUTES = SETTINGS.base.security.get(
        "access_token_expire_minutes", 60
    )  # 60 * 24  # (60 minutes x 24 Hours)
else:
    ACCESS_TOKEN_URL = "token"
    ACCESS_TOKEN_EXPIRE_MINUTES = 15
    raise Exception(MESSAGE)
