# -*- coding: utf-8 -*-
"""
    API - CRUD
"""

# Fastberry
from fastberry import GQL, Fastberry, to_camel_case
from .. import types

SETTINGS = Fastberry()

""" All-Operations
query operations {
  query: operationQuery
  mutation: operationMutation
}
"""

# Create your API (GraphQL) here.
class Operations(GQL):
    """Operations Api"""

    class Query:
        """Query"""
        
        async def app_operations(info) -> list[types.Operation]:
            """## List of All GraphQL Operations"""
            # print(info)
            items = []
            for x in SETTINGS.apps.operations.query:
                active = types.Operation(name = to_camel_case(x), type="Query")
                items.append(active)
            for x in SETTINGS.apps.operations.mutation:
                active = types.Operation(name = to_camel_case(x), type="Mutation")
                items.append(active)
            return items