# -*- coding: utf-8 -*-
from typing import Union

PRETRAINED = [
    'bert',
    'xlnet',
    'electra',
]


META_TAGS = ('SI', 'TR', 'WR', 'MN')


class EntityMeta:
    def __init__(self, meta_entities) -> None:
        self._entities = meta_entities
        self._counter = {tag: len(meta_entities.get(tag, [])) for tag in META_TAGS}

    def to_params(self):
        return {f"n_{tag.lower()}": cnt for tag, cnt in self._counter.items()}

    def count_tag(self, tag):
        return self._counter.get(tag, 0)

    def count_meta_tags(self):
        return [self._counter.get(tag, 0) for tag in META_TAGS]

    def __str__(self) -> str:
        return ', '.join([f"n_{tag.lower()}: {cnt}" for tag, cnt in self._counter.items()])

    def __repr__(self) -> str:
        return self.__str__()


class Entity:
    def __init__(self,
                 idx: int,
                 tag: str,
                 val: str,
                 i: int,
                 j: int,
                 start: int,
                 end: int):
        super().__init__()
        self.idx = idx
        self.tag = tag
        self.val = val
        self.i = i
        self.j = j
        self.start = start
        self.end = end

    def __str__(self):
        return f"[{self.val}/{self.tag}] #{self.idx} ({self.i+1}, {self.j}) [{self.start}:{self.end}]"

    def __repr__(self):
        return self.__str__()

    def __lt__(self, other):
        assert isinstance(other, Entity)
        return self.i < other.i


class Degrees:
    def __init__(self, outs_any: dict, outs_tag: dict) -> None:
        self.outs_any = outs_any
        self.outs_tag = outs_tag

    def get_outs_any(self, idx: int):
        return self.outs_any.get(idx)

    def get_outs_tag(self, s_idx: int, o_tag: str):
        return self.outs_tag.get((s_idx, o_tag))

    def get_d_any(self, idx: int):
        return len(self.get_outs_any(idx) or [])

    def get_d_tag(self, s_idx: int, o_tag: str):
        return len(self.get_outs_tag(s_idx, o_tag) or [])


class Issue:
    def __init__(self, key, s: Entity, o: Entity, relation: Union[str, list], msg=None) -> None:
        self.key = key
        self.s = s
        self.o = o
        self.relation = relation if isinstance(relation, str) else '|'.join(relation)
        self.msg = msg

    def __str__(self) -> str:
        rel = f"[{self.s.val}] --{self.relation}--> [{self.o.val}]"
        return f"[{self.key}] {self.s.tag} -> {self.o.tag}, ({self.s.i+1} -> {self.o.i+1}), {rel} ||| {self.msg or ''}"

    def __repr__(self) -> str:
        return self.__str__()
