from __future__ import annotations

import typing

import mongoengine as me

from .base_document import BaseDocument
from .base_model import BaseModel
from ..utils import cast

ObjectT = typing.TypeVar('ObjectT', bound='MyObject')


def get_model_name(obj: BaseModel | type[BaseModel]):
    if isinstance(obj, BaseModel):
        return obj.__class__.__name__
    return obj.__name__


class CurrentObject(BaseDocument):
    user_id: int = me.IntField()
    model: str = me.StringField()
    obj: dict = me.DictField()

    meta = {
        'collection': 'CurrentObjects',
    }


class CollectionObject(BaseDocument):
    user_id: int = me.IntField()
    model: str = me.StringField()
    obj: dict = me.DictField()

    meta = {
        'collection': 'CollectionObjects',
    }


class UserProxy(typing.Generic[ObjectT]):

    def __init__(self, obj: ObjectT):
        self.obj = obj

    def __enter__(self) -> ObjectT:
        return self.obj

    def __exit__(self, exc_type, exc_value, trace):
        self.obj.save()


class UserProxyModel(BaseModel):
    """ Base class for all project objects """

    @classmethod
    def get(cls: type[ObjectT]) -> ObjectT | None:
        """ Get current object of current user from storage """
        from ..context import ctx

        doc = CurrentObject.get_doc(user_id=ctx.user_id, model=get_model_name(cls))

        if doc is None:
            return None
        else:
            return cast(doc.obj, cls)

    @classmethod
    def delete(cls: type[ObjectT]) -> None:
        """ Delete current object of current user from storage """
        from ..context import ctx

        doc = CurrentObject.get_doc(user_id=ctx.user_id, model=get_model_name(cls))

        if doc:
            doc.delete()

    def save(self: ObjectT) -> ObjectT:
        """ Save object to storage as current for current user """
        from ..context import ctx

        doc = CurrentObject.get_doc(user_id=ctx.user_id, model=get_model_name(self))

        if doc is None:
            doc = CurrentObject(user_id=ctx.user_id, model=get_model_name(self))

        doc.obj = cast(self, dict)
        doc.save()

        return self

    @classmethod
    def proxy(cls: type[ObjectT]) -> UserProxy[ObjectT]:
        """
        (ContextManager)
        On enter: return newly created or current object of current user from storage;
        On exit: save object to storage as current for current user;
        """
        return UserProxy(cls.get() or cls())

    @classmethod
    def get_collection(cls: type[ObjectT]) -> list[ObjectT]:
        """ Get objects collection of current user from storage """
        from ..context import ctx

        docs = CollectionObject.get_docs(user_id=ctx.user_id, model=get_model_name(cls))
        return cast([doc.obj for doc in docs], list[cls])

    def save_to_collection(self: ObjectT) -> ObjectT:
        """ Save object to storage collection for current user """
        from ..context import ctx

        CollectionObject(
            user_id=ctx.user_id,
            model=get_model_name(self),
            obj=cast(self, dict)
        ).save()

        return self

    def replace_in_collection(self: ObjectT, key: str) -> ObjectT:
        """ Replace object in storage collection for current user by given key """
        from ..context import ctx

        docs = CollectionObject.get_docs(user_id=ctx.user_id, model=get_model_name(self))

        for doc in docs:
            if doc.obj[key] == getattr(self, key):
                doc.obj = cast(self, dict)
                doc.save()

        return self
