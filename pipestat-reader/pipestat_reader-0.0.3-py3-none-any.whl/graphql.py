import os
from typing import Dict, List, Optional, Tuple, Union

import graphene
import pipestat
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyConnectionField, SQLAlchemyObjectType
from graphene_sqlalchemy.registry import get_global_registry
from graphene_sqlalchemy_filter import FilterableConnectionField, FilterSet
from sqlalchemy.inspection import inspect

from ._version import __version__
from .const import FILTERS_BY_CLASS, PACKAGE_NAME


class CountableConnection(graphene.relay.Connection):
    class Meta:
        abstract = True

    total_count = graphene.Int()

    @staticmethod
    def resolve_total_count(root, info):
        return root.length


class PipestatReader(dict):
    def __init__(self, pipestat_managers: List[pipestat.PipestatManager]):
        super(PipestatReader, self).__init__()
        self.pipestat_managers_dict = {psm.namespace: psm for psm in pipestat_managers}
        for namespace, pipestat_manager in self.pipestat_managers_dict.items():
            self.setdefault(namespace, {})
            self[namespace]["pipestat_manager"] = pipestat_manager
            self[namespace]["table_name"] = pipestat_manager.namespace
            self[namespace]["table_model"] = pipestat_manager.get_orm(
                table_name=self[namespace]["table_name"]
            )
        # the repeated loop is needed so we can get access to all the mappers
        for namespace, pipestat_manager in self.pipestat_managers_dict.items():
            meta = type(
                "Meta",
                (),
                {
                    "model": self[namespace]["table_model"],
                    "interfaces": (relay.Node,),
                    "connection_class": CountableConnection,
                    "description": f"*{self[namespace]['table_name']}* table model generated with "
                    f"`{PACKAGE_NAME} v{__version__}`",
                },
            )
            meta_filter = type(
                "Meta",
                (),
                {
                    "model": self[namespace]["table_model"],
                    "fields": {
                        c.name: FILTERS_BY_CLASS[c.type.__class__.__name__]
                        for c in self[namespace]["table_model"].__table__.columns
                    },
                },
            )

            attrs = {"Meta": meta}
            relationships = inspect(self[namespace]["table_model"]).relationships
            obj_name = (
                f"{self[namespace]['table_name'].capitalize()}SQLAlchemyObjectType"
            )
            if len(relationships.keys()):
                for r in relationships.keys():
                    attrs.update(
                        {r: f"{PACKAGE_NAME}.{os.path.basename(__file__)}.{obj_name}"}
                    )

            self[namespace]["SQLAlchemyObjectType"] = type(
                obj_name,
                (SQLAlchemyObjectType,),
                attrs,
            )
            self[namespace]["filter"] = type(
                f"{self[namespace]['table_name'].capitalize()}Filter",
                (FilterSet,),
                {"Meta": meta_filter},
            )

    @property
    def query(self) -> type:
        attrs = {"node": relay.Node.Field()}
        for namespace in self.pipestat_managers_dict.keys():
            attrs.update(
                {
                    f"{namespace}": FilterableConnectionField(
                        self[namespace]["SQLAlchemyObjectType"].connection,
                        filters=self[namespace]["filter"](),
                    )
                }
            )
        return type(
            f"{'__'.join(list(self.pipestat_managers_dict.keys()))}Query",
            (graphene.ObjectType,),
            attrs,
        )

    def generate_graphql_schema(self) -> graphene.Schema:
        return graphene.Schema(query=self.query)
