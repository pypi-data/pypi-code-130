from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import md5

import mongoengine as me

from ..new.translations import Translations
from ...base import BaseDocument, NewObject


class CallbackButtonDoc(BaseDocument):
    hash: str = me.StringField(primary_key=True)
    text: str = me.StringField()
    button_id: str = me.StringField()
    vars: dict = me.DictField()

    meta = {
        'collection': 'CallbackButtons'
    }


@dataclass
class CallbackButton(NewObject):
    """ CallbackButton """
    text: str | Translations
    id: str = None
    vars: dict = field(default_factory=dict)

    def __getitem__(self, item):
        return self.vars[item]

    def get_hash(self) -> str:
        string = f'{self.text}|{self.id}|{self.vars}'
        return md5(string.encode()).hexdigest()

    @classmethod
    def get(cls, doc_id: str) -> CallbackButton | None:
        doc = CallbackButtonDoc.get_doc(hash=doc_id)
        if not doc:
            return None
        return CallbackButton(text=doc.text, id=doc.button_id, vars=doc.vars)

    def __post_init__(self):
        self.id = self.id or str(self.text)
        btn_hash = self.get_hash()

        CallbackButtonDoc(
            hash=btn_hash,
            text=str(self.text),
            button_id=self.id,
            vars=self.vars,
        ).save()

        self.doc_id = btn_hash

    def __call__(self, **_vars) -> CallbackButton:
        """ Return button copy [text=text.format(**_vars), id=id.format(**_vars), vars=_vars] """
        return CallbackButton(self.text.format(**_vars), self.id, vars=_vars)
