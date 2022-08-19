from datetime import datetime
from typing import Optional

import pydantic

from RCC.types import base
from RCC.exceptions import PlayerInfoNotFound, RCCStatusError


class RCCCheck(base.BaseModel):
    moder_steamid: int = pydantic.Field(alias="moderSteamID")
    time: datetime
    server_name: Optional[str] = pydantic.Field(default=None, alias="serverName")


class RCCBan(base.BaseModel):
    ban_id: int = pydantic.Field(default=None, alias="banID")
    reason: str
    ban_date: datetime = pydantic.Field(alias="banDate")
    unban_date: datetime = pydantic.Field(alias="unbanDate")
    server_name: Optional[str] = pydantic.Field(default=None, alias="serverName")
    ovh_server_id: Optional[int] = pydantic.Field(default=None, alias="OVHserverID")
    active: bool

    @pydantic.validator("reason")
    def strip_resason(cls, reason: str):
        return reason.strip()


class RCCPlayer(base.BaseModel):
    steamid: int
    rcc_checks: int
    checks: Optional[list[RCCCheck]] = pydantic.Field(default=None, alias="last_check")
    last_ip: Optional[list[str]] = None
    last_nick: Optional[str] = None
    another_accs: Optional[list[int]] = None
    bans: Optional[list[RCCBan]] = None
    proofs: Optional[list[str]] = None

    @pydantic.root_validator(pre=True)
    def check_status(cls, values):
        status = values.get("status")
        if status == "error":
            error = values.get("errorreason")
            if error == pydantic.ErrorTypes.player_not_found.value:
                raise PlayerInfoNotFound(error)
            else:
                raise RCCStatusError(error)
        return values


__all__ = ("RCCPlayer", "RCCBan", "RCCCheck")
