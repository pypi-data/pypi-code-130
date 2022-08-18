# -*- coding: utf-8 -*-
""" [Extension]
    Inject { User } or { Anonymous-User } to GraphQL Context.
"""
import types

from fastberry import BaseExtension

from .actions import User
from .actions.security import AccessToken


async def get_request_user(request):
    """Get User from Request the Header or Cookie"""
    token = request.headers.get("authorization", "").replace("Bearer ", "")
    user = await User.verify_token(token)
    return user


class InjectUser(BaseExtension):
    """Inject User Extension"""

    async def on_executing_start(self):
        request = self.execution_context.context.get("request")
        token = await get_request_user(request)
        # Set-User (Context)
        self.execution_context.context["user"] = token.user
