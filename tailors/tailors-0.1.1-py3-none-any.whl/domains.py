# -*- coding: utf-8 -*-
import itertools
from dataclasses import dataclass
from typing import List, Optional, Union

import hao


class Derivable:

    @classmethod
    def subclasses(cls):
        all_subclasses = []
        for subclass in cls.__subclasses__():
            all_subclasses.append(subclass)
            all_subclasses.extend(subclass.subclasses())
        return all_subclasses


class Tags:
    __slot__ = ['tag2id', 'id2tag', 'n_tags', 'supporting_tags', 'supporting_tag_ids', 'trivial_tag', 'trivial_tag_id']
    def __init__(self,
                 tags: List[str],
                 supporting_tags: Optional[List[str]] = None,
                 trivial_tag: str = 'O',
                 is_bies = False) -> None:
        supporting_tags = supporting_tags or []
        self.tag2id, self.id2tag, self.n_tags = self.build_mappings(tags, supporting_tags, trivial_tag, is_bies)
        self.supporting_tags = set(supporting_tags)
        self.supporting_tag_ids = set([self.tag2id[tag] for tag in supporting_tags])
        self.trivial_tag = trivial_tag
        self.trivial_tag_id = self.tag2id[trivial_tag]

    @staticmethod
    def build_mappings(tags: List[str],
                       supporting_tags: Optional[List[str]] = None,
                       trivial_tag: str = 'O',
                       is_bies = False):
        assert tags is not None and len(tags) > 0, 'expecting `tags` of list of str'
        assert trivial_tag not in tags, '`tags` should not contain `trivial_tag`'
        if supporting_tags:
            assert all(tag not in tags for tag in supporting_tags), '`tags` should not contain any of `supporting_tags`'

        tags, supporting_tags = hao.lists.uniquify(tags), hao.lists.uniquify(supporting_tags)
        if is_bies:
            prefixes = ('B-', 'I-', 'E-', 'S-')
            tags = [f"{prefix}{tag}" for tag, prefix in itertools.product(tags, prefixes)]
        tags_all = tags + (supporting_tags or []) + [trivial_tag]

        tag2id = {tag: i for i, tag in enumerate(tags_all)}
        id2tag = {i: tag for i, tag in enumerate(tags_all)}
        return tag2id, id2tag, len(tags_all)

    def get_id_by_tag(self, tag: str, default=None, ignore_supporting=False):
        if ignore_supporting and tag in self.supporting_tag:
            return self.trivial_tag_id
        return self.tag2id.get(tag, default or self.trivial_tag_id)

    def get_ids_by_tags(self, tags: List[str], default=None, ignore_supporting=False, drop_supporting=False):
        return [self.get_id_by_tag(tag, default, ignore_supporting) for tag in tags if not drop_supporting or tag not in self.supporting_tags]

    def get_tag_by_id(self, _id: int, default=None, ignore_supporting=False):
        if ignore_supporting and _id in self.supporting_tag_ids:
            return self.trivial_tag
        return self.id2tag.get(_id, default or self.trivial_tag)

    def get_tags_by_ids(self, ids: List[int], default=None, ignore_supporting=False, drop_supporting=False):
        return [self.get_tag_by_id(_id, default, ignore_supporting) for _id in ids if not drop_supporting or _id not in self.supporting_tag_ids]

    def is_supporting_tag(self, tag: str):
        return tag in self.supporting_tags

    def is_supporting_tag_id(self, _id):
        return _id in self.supporting_tag_ids

    def is_not_supporting_tag_id(self, _id):
        return not self.is_supporting_tag_id(_id)

@dataclass
class Factor:
    factor: float
    min_val: float = 1e-10
    max_val: float = 1e-1

    def apply(self, v: Union[int, float]):
        val = self.factor * v
        if self.min_val:
            val = max(self.min_val, val)
        if self.max_val:
            val = min(self.max_val, val)
        return val
