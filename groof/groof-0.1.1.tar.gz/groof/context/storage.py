from __future__ import annotations

import mongoengine as me

from ..base import BaseDocument


class Storage(BaseDocument):
    key: int = me.IntField()
    state: str = me.StringField()
    lang: str = me.StringField()
    data: dict = me.DictField()

    @classmethod
    def get(cls, user_id: int) -> Storage:
        return cls.get_doc(key=user_id) or Storage(key=user_id).save()

    meta = {
        'collection': 'Storage'
    }
