from core.dal import UserView

from ..services.auth import get_validator, DoorsCachedToken, require_wsauth


class UsersGroup:

    def __init__(self, server):
        self.server = server

    async def authenticate(self, data, client):
        validator = get_validator()
        tk: DoorsCachedToken = validator.authenticate_token(data.token)

        if tk is None:
            return { "authenticated": False, "err": "invalid_token" }
        elif validator.token_expired(tk):
            return { "authenticated": False, "err": "token_expired" }
        elif validator.token_revoked(tk):
            return { "authenticated": False, "err": "token_revoked" }
        elif validator.scope_insufficient(tk, tk.get_scope()):
            return { "authenticated": False, "err": "scope_insufficient" }
        elif validator.scope_insufficient(tk, tk.get_scope()):
            return { "authenticated": False, "err": "scope_insufficient" }

        # assign authenticated status to WS client
        client.token = tk
        client.user = UserView(**tk.user.view_public)

        # @todo: @later: rethink if we should store references between user/client?
        client.user.client = client

        return {
            "authenticated": True,
            "uid": client.user.uid
        }

    @require_wsauth
    async def me(self, user):
        # test method to check stuff

        return {
            'uid': user.uid,
            'username': user.username,
            # 'wid': user.wid,
            # 'iso': user.iso,
        }
