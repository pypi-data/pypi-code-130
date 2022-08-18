# -*- coding: utf-8 -*-
"""
    API - CRUD
"""

import functools


# Fastberry
from fastberry import GQL
from fastberry.graphql.types import Error, ErrorMessage, Mutation, Query
from fbauth import types
from fbauth.actions.users import User

from ..types import AccessToken

from .. import types
from ..actions.users import User
from ..database import SQL

sql_manager = SQL(types.User)


# Create your API (GraphQL) here.
class Accounts(GQL):
    """Demo Api"""

    schema = types.User

    class Query:
        """Query"""

        async def me(info) -> Query(types.User):
            """## Get Current User(Me)"""
            account = info.context.get("user")
            user = None
            if account:
                user = types.User(
                    id=account.id,
                    username=account.username,
                    password=None,
                    email=account.email,
                    is_disabled=account.is_disabled,
                    is_staff=account.is_staff,
                    is_super_user=account.is_super_user,
                    created_on=account.created_on,
                    role_id=account.role_id,
                )
            return user
        
    class Mutation:
        """Mutation"""

        async def create(
            username: str, password: str, email: str
        ) -> Mutation(types.User):
            """## Create Account"""
            message = "Something went wrong!"
            results = await User.create(
                username=username, password=password, email=email, role_id=1
            )
            if not results.error:
                item = results.data.__dict__
                item["password"] = None
                return types.User(**item)
            if (
                "UNIQUE" in results.error_message
                and "username" in results.error_message
            ):
                message = "Username is taken."
            elif "UNIQUE" in results.error_message and "email" in results.error_message:
                message = "Email is already registered."
            return Error([ErrorMessage(type="input", message=message)])

        async def login(
            password: str, username: str | None = None, email: str | None = None
        ) -> Mutation(AccessToken):
            """## User Login"""
            user_selector = "username"
            if email:
                user_selector = "email"
                found_user = await User.get_by(email=email)
                if found_user:
                    username = found_user.username
            access = await User.authenticate(username=username, password=password)
            # ... on Success
            if access.is_valid:
                return AccessToken(token=access.token)
            # ... on Error
            message = f"Invalid {user_selector} or password."
            return Error([ErrorMessage(type="credentials", message=message)])

