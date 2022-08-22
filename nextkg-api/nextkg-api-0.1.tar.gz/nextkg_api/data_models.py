import datetime as dt
from typing import Any, List, Union

from pydantic import BaseModel


class Property(BaseModel):
    name: str
    value: Any = None
    json_value: Union[str, List[str]] = None


class EntityMeta(BaseModel):
    pv: int = None
    ts: dt.datetime = None
    origin_id: str = None
    md5: str = None
    edit_user: str = None
    audit_user: str = None
    domain: Union[str, List[str]] = None


class Entity(BaseModel):
    id: str = None
    entity_name: str
    entity_type: str = None
    entity_tags: Union[str, List[str]] = None
    properties: List[Property] = None
    create_time: dt.datetime = None
    meta: EntityMeta = None
    version: str = None


class PartialEntity(Entity):
    entity_name: str = None


class Relation(BaseModel):
    start_entity_id: str = None
    end_entity_id: str = None
    relation_type: str


class Neighbor(BaseModel):
    entity: Entity
    relation_type: str
