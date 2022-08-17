# -*- coding: utf-8 -*-
"""
    API - CRUD
"""

# Fastberry
import strawberry
from fastberry import GQL
from fastberry.graphql.inputs import Pagination
from fastberry.graphql.types import (
    Edges,
    Error,
    ErrorMessage,
    Mutation,
    Query,
    Response,
)

from .. import types
from ..database import SQL

sql_manager = SQL(types.Role)

# Create your API (GraphQL) here.
class Roles(GQL):
    """Roles Api"""

    schema = types.Role

    class Query:
        """Query"""

        async def search(
            pagination: Pagination | None = None,
            name: str | None = None,
        ) -> Edges(types.Role):
            """## Search for Roles by Name"""
            pagination = pagination or Pagination()
            pagination = pagination.init()
            results = await sql_manager.search(
                columns=["name"],
                value=name,
                page=pagination.page,
                limit=pagination.limit,
                sort_by=pagination.sort_by,
            )
            return Response(
                edges=[types.Role(**item.__dict__) for item in results.data],
                length=results.count,
                pages=results.pages,
            )

        async def detail(info, id: strawberry.ID) -> Query(types.Role):
            """## Get Role by ID"""
            item = await sql_manager.detail(id)
            if item:
                return types.Role(**item.__dict__)
            return None

        async def all(info) -> list[types.Role]:
            """## Get All Roles"""
            items = await sql_manager.all()
            if items.data:
                return [types.Role(**item.__dict__) for item in items.data]
            return []

    class Mutation:
        """Mutation"""

        async def create(name: str) -> Mutation(types.Role):
            """## Create Role"""
            message = "Something went wrong!"
            results = await sql_manager.create({"name": name})
            if not results.error:
                return types.Role(**results.data.__dict__)
            if "UNIQUE" in results.error_message:
                message = "Role name is taken."
            return Error([ErrorMessage(type="input", message=message)])

        async def update(id: strawberry.ID, name: str) -> Mutation(types.Role):
            """## Change Role Name"""
            # print(info.context.get("user"))
            results = await sql_manager.update([id], name=name)
            if not results.error:
                return types.Role(**results.data.__dict__)
            return Error([ErrorMessage(type="input", message="Something went wrong!")])

        async def delete(id: list[strawberry.ID]) -> int:
            """## Delete Role"""
            results = await sql_manager.delete(id)
            return results.count

        async def edit_perms(
            id: strawberry.ID, perms: list[str]
        ) -> Mutation(types.Role):
            """## Add/Remove Permissions to Role"""
            # print(info.context.get("user"))
            results = await sql_manager.update([id], perms=perms)
            if not results.error and results.data:
                return types.Role(**results.data.__dict__)
            elif not results.error and not results.data:
                return types.Role(id=None, _id=None, perms=[], name=None)
            return Error([ErrorMessage(type="input", message="Something went wrong!")])
