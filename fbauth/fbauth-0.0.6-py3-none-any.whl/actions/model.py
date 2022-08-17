"""
    [Users and Tokens]
"""

import dataclasses as dc
import typing


@dc.dataclass
class AccountManager:
    _id: str | None = None
    id: str | None = None
    role_id: typing.Any = None
    username: str | None = None
    email: str | None = None
    password: str | None = None
    is_disabled: bool = False
    is_staff: bool = False
    is_super_user: bool = False
    is_authenticated: bool = False
    is_anonymous: bool = False
    created_on: typing.Any = None


@dc.dataclass
class Token:
    is_valid: bool = False
    token: typing.Any = None
    user: typing.Any = None
