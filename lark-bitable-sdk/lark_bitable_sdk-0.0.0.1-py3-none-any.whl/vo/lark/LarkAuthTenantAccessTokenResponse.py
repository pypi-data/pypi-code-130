from pydantic import BaseModel

from vo.lark.LarkBaseResponse import LarkBaseResponse


class LarkAuthTenantAccessTokenResponse(LarkBaseResponse, BaseModel):
    expire: int
    tenant_access_token: str
