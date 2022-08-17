# -*- coding: utf-8 -*-
""" [Permission]
    Check GraphQL Context for a { User } or { Anonymous-User }.
"""

import json
import typing
from pathlib import Path

from fastberry import BasePermission
from strawberry.types import Info

from .actions import User


def write_public_perms(path_to_file: str):
    """Writing to Public-API (JSON)"""
    path = Path(path_to_file)
    if not path.is_file():
        with open(path_to_file, "w") as outfile:
            data = {"perms": []}
            json_object = json.dumps(data, indent=4)
            outfile.write(json_object)


def read_public_perms():
    """Read Public-API Permissions"""
    path_to_file = "api-public-perms.json"
    write_public_perms(path_to_file)
    json_dict = {"perms": []}
    with open(path_to_file, "r") as outfile:
        data = outfile.read()
        perms = None
        if data:
            json_dict = json.loads(data)
            perms = json_dict.get("perms")
        if not isinstance(perms, list):
            json_dict = {"perms": []}
    return json_dict["perms"]


PUBLIC_PERMS = read_public_perms()


class IsAuthorized(BasePermission):
    """Check If User Is Authorized"""

    message = "User is not authorized"  # Unauthorized

    async def has_permission(self, source: typing.Any, info: Info, **kwargs) -> bool:
        """Check GraphQL's Info Context"""

        operation = info.field_name  # info.python_name
        user = info.context.get("user")
        public_perms = PUBLIC_PERMS or []
        if user:
            if user.is_super_user:
                return True
            elif user.is_anonymous:
                return operation in public_perms
            else:
                permissions = await User.get_perms(user.role_id)
                print(public_perms)
                all_permissions = set(permissions + public_perms)
                return operation in all_permissions
