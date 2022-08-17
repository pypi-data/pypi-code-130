#!/usr/bin/env python3
from dataclasses import dataclass, field
from typing import Optional


@dataclass(order=True, frozen=True)
class Residue:
    chain_id: str
    number: int


@dataclass(order=True)
class Contig:
    chain_id: str
    start: int
    stop: int
    contig_id: Optional[int] = field(default=None, init=False)
    model_id: Optional[int] = field(default=None, init=False)

    def __len__(self):
        return self.stop - self.start

    def residues(self) -> list[Residue]:
        return [Residue(self.chain_id, r) for r in range(self.start, self.stop)]


@dataclass
class ContigGroup:
    contigs: list[Contig] = field(default_factory=list)
    model_id: Optional[int] = None

    def get_contigs(self) -> list[Contig]:
        return self.contigs


@dataclass
class Loop(Contig):
    pass


@dataclass
class Helix(Contig):
    pass


@dataclass
class Strand(Contig):
    sheet_id: str


@dataclass
class RNAStrand(Contig):
    pass


@dataclass
class RNAHelix(ContigGroup):
    """An RNA helix"""


class RNAModel:
    def __init__(self, models):
        self.models = []
        self._rigid_bodies = []
        for model in models:
            self.add_model(model)
        self._add_contig_ids()

    def rigid_bodies(self):
        return self._rigid_bodies

    # RNA doesn't have loops
    def get_loop(self, _contig_id):
        return None

    def add_model(self, model):
        model.model_id = len(self.models)
        self.models.append(model)
        self._rigid_bodies.append(model)
        if isinstance(model, RNAHelix):
            for child in model.get_contigs():
                self.add_child_model(child)

    def add_child_model(self, child):
        child.model_id = len(self.models)
        self.models.append(child)

    def _add_contig_ids(self):
        strands = [m for m in self.models if isinstance(m, RNAStrand)]
        strands.sort()

        for index, strand in enumerate(strands):
            strand.contig_id = index


@dataclass
class Sheet(ContigGroup):
    """A Sheet, a collection of strands."""

    def add_strand(self, strand):
        self.contigs.append(strand)


class ProteinModel:
    def __init__(self):
        self.models = []
        self.contigs = 0
        self.sheets = {}

    def get_loop(self, contig_id):
        for model in self.models:
            if isinstance(model, Loop) and model.contig_id == contig_id:
                return model
        return None

    def rigid_bodies(self):
        """Returns helices and sheets"""
        return [m for m in self.models if isinstance(m, (Helix, Sheet))]

    def _get_sheet(self, sheet_id):
        if self.sheets.get(sheet_id) is None:
            sheet = Sheet()
            sheet.model_id = len(self.models)
            self.models.append(sheet)
            self.sheets[sheet_id] = sheet.model_id
        return self.models[self.sheets[sheet_id]]

    def _next_contig_id(self):
        contig_id = self.contigs
        self.contigs += 1
        return contig_id

    def add_contig(self, contig):
        contig.contig_id = self._next_contig_id()
        contig.model_id = len(self.models)
        self.models.append(contig)
        if isinstance(contig, Strand):
            sheet = self._get_sheet(contig.sheet_id)
            sheet.add_strand(contig)
