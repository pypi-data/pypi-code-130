from __future__ import annotations

import typing
from dataclasses import dataclass

import bson
import mongoengine as me

from .base_document import BaseDocument
from .base_model import BaseModel
from ..utils import cast

ModelT = typing.TypeVar('ModelT', bound='UserModel')


def get_model_name(obj: UserModel | type[UserModel]):
    if isinstance(obj, UserModel):
        return obj.__class__.__name__
    return obj.__name__


class UserModelDocument(BaseDocument):
    user_id: int = me.IntField(required=True)
    model: str = me.StringField(required=True)
    committed: bool = me.BooleanField(default=False)
    current: bool = me.BooleanField(default=False)
    data: dict = me.DictField()

    meta = {
        'collection': '__UserModels__',
    }


@dataclass
class UserModel(BaseModel):
    id: bson.ObjectId = None

    # TODO
    # def __init__(self, **attrs):
    #     fields = list(self.__class__.__annotations__) + ['id']
    #
    #     for field in fields:
    #         setattr(self, field, attrs.pop(field, None))
    #
    #     if attrs:
    #         attrs_names = list(attrs)
    #         model_name = get_model_name(self)
    #         raise ValueError(f'Unexpected attrs {attrs_names} for model {model_name}')

    @classmethod
    def make_query(cls, filters: dict) -> dict:
        from ..context import ctx

        filters = {f'data__{key}': value for key, value in filters.items()}
        return {'user_id': ctx.user_id, 'model': get_model_name(cls)} | filters

    @classmethod
    def find(cls: type[ModelT], **filters) -> ModelT | None:
        doc = UserModelDocument.get_doc(**cls.make_query(filters))

        if doc is None:
            return None
        else:
            return cast(doc.data | {'id': doc.id}, cls)

    @classmethod
    def find_all(cls: type[ModelT], **filters) -> list[ModelT]:
        docs = UserModelDocument.get_docs(**cls.make_query(filters))
        return cast([doc.data | {'id': doc.id} for doc in docs], list[cls])

    def save(self: ModelT, as_current: bool = False) -> ModelT:
        from ..context import ctx

        doc = UserModelDocument(user_id=ctx.user_id, model=get_model_name(self))

        if as_current:
            query = {'user_id': ctx.user_id, 'model': get_model_name(self), 'current': True}
            prev_doc = UserModelDocument.get_doc(**query)

            if prev_doc:
                prev_doc.current = False
                prev_doc.save()

            doc.current = True

        doc.data = cast(self, dict)
        doc.id = self.id
        self.id = doc.save().id
        return self

    def delete(self: ModelT) -> None:
        UserModelDocument(id=self.id).delete()

    @classmethod
    def current(cls) -> ModelT | None:
        from ..context import ctx

        query = {'user_id': ctx.user_id, 'model': get_model_name(cls), 'current': True}
        doc = UserModelDocument.get_doc(**query)

        if doc is None:
            return None
        else:
            return cast(doc.data | {'id': doc.id}, cls)
