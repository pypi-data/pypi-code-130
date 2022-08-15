from __future__ import annotations

from collections import defaultdict

from .context_dict import ContextDict
from .layer2 import ContextLayer2
from .storage import Storage
from ..objects import CallbackButton


def storage_property(name: str):
    def fget(self: ContextLayer3):
        memory_storage = self._memory_storage

        if name not in memory_storage:
            storage = self._storage
            value = getattr(storage, name)
            memory_storage[name] = value

        return memory_storage[name]

    def fset(self: ContextLayer3, value):
        storage = self._storage
        setattr(storage, name, value)
        storage.save()

        self._memory_storage[name] = value

    return property(fget, fset)


class ContextLayer3(ContextLayer2):
    def __init__(self):
        self.__memory_storage = defaultdict(dict)

    @property
    def _memory_storage(self):
        return self.__memory_storage[self.user_id]

    @property
    def _storage(self):
        return Storage.get(self.user_id)

    @property
    def data(self):
        return ContextDict(self._storage)

    lang: str | None = storage_property('lang')
    state: str | None = storage_property('state')

    @property
    def button(self) -> CallbackButton | None:
        """ CallbackQuery.button """
        try:
            doc_id = self.callback_query.data
            return CallbackButton.get(doc_id)
        except (KeyError, AttributeError):
            return None

    def delete_current_models(self):
        from ..base.user_proxy_model import CurrentObject

        for doc in CurrentObject.get_docs(user_id=self.user_id):
            doc.delete()
