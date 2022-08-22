# SPDX-License-Identifier: GPL-2.0-or-later OR AGPL-3.0-or-later OR CERN-OHL-S-2.0+
import abc
from typing import Tuple, Dict, Generic, Optional, TypeVar, cast

from ..typing import IntFloat, SingleOrMulti, OptSingleOrMulti
from .. import _util
from ..technology import geometry as geo, primitive as prm, technology_ as tch
from . import layout as lay, circuit as ckt


__all__ = ["RoutingGauge", "Library", "StdCellLibrary"]


LibraryType = TypeVar("LibraryType", bound="Library")


class _Cell(Generic[LibraryType]):
    def __init__(self, *, lib: LibraryType, name: str):
        self.lib = lib
        self.name = name

        self.circuits = ckt._Circuits()
        self.layouts = _CellLayouts()

    @property
    def tech(self):
        return self.lib.tech
    @property
    def cktfab(self):
        return self.lib.cktfab
    @property
    def layoutfab(self):
        return self.lib.layoutfab

    @property
    def circuit(self):
        try:
            return self.circuits[self.name]
        except KeyError:
            raise ValueError(f"Cell '{self.name}' has not default circuit")

    @property
    def layout(self):
        try:
            return self.layouts[self.name]
        except KeyError:
            raise ValueError(f"Cell '{self.name}' has not default layout")

    def new_circuit(self, *, name: Optional[str]=None):
        if name is None:
            name = self.name
        
        circuit = self.cktfab.new_circuit(name)
        self.circuits += circuit
        return circuit

    def add_layout(self, *, layout: "lay._Layout", name: Optional[str]=None):
        if name is None:
            name = self.name
        self.layouts += _CellLayout(name=name, layout=layout)

    def new_circuitlayouter(self, *,
        name: Optional[str]=None, boundary: Optional[geo._Rectangular]=None,
    ) -> "lay._CircuitLayouter":
        if name is None:
            name = self.name
        if not isinstance(name, str):
            raise TypeError("name has to be a string")
        try:
            circuit = self.circuits[name]
        except KeyError:
            raise ValueError(f"circuit with name '{name}' not present")

        layouter = self.lib.layoutfab.new_circuitlayouter(
            circuit=circuit, boundary=boundary,
        )
        self.layouts += _CellLayout(name=name, layout=layouter.layout)
        return layouter

    @property
    def subcells_sorted(self):
        cells = set()
        for circuit in self.circuits:
            for cell in circuit.subcells_sorted:
                if cell not in cells:
                    yield cell
                    cells.add(cell)


class _OnDemandCell(_Cell[LibraryType], abc.ABC, Generic[LibraryType]):
    """_Cell with on demand circuit and layout creation
    
    The circuit and layout will only be generated the first time it is accessed.
    """
    @property
    def circuit(self):
        try:
            return self.circuits[self.name]
        except KeyError:
            self._create_circuit()
            try:
                return self.circuits[self.name]
            except:
                raise NotImplementedError(
                    f"Cell '{self.name}' default circuit generation"
                )

    @property
    def layout(self):
        try:
            return self.layouts[self.name]
        except KeyError:
            self._create_layout()
            try:
                return self.layouts[self.name]
            except:
                raise NotImplementedError(
                    f"Cell '{self.name}' default layout generation"
                )

    @abc.abstractmethod
    def _create_circuit(self):
        pass

    @abc.abstractmethod
    def _create_layout(self):
        pass


class _Cells(_util.TypedListStrMapping[_Cell[LibraryType]], Generic[LibraryType]):
    @property
    def _elem_type_(self):
        return _Cell


class _CellLayout:
    def __init__(self, *, name: str, layout: "lay._Layout"):
        self.name = name
        self.layout = layout


class _CellLayouts(_util.TypedListStrMapping[_CellLayout]):
    @property
    def _elem_type_(self):
        return _CellLayout

    def __getitem__(self, item: str) -> "lay._Layout":
        elem = super().__getitem__(item)
        assert isinstance(elem, _CellLayout)
        return elem.layout


class RoutingGauge:
    directions = frozenset(("horizontal", "vertical"))

    def __init__(self, *,
        tech: tch.Technology,
        bottom: prm.MetalWire, bottom_direction: str, top: prm.MetalWire,
        pitches: Dict[prm.MetalWire, IntFloat]={},
        offsets: Dict[prm.MetalWire, IntFloat]={},
    ):
        self.tech = tech

        metals = tuple(tech.primitives.__iter_type__(prm.MetalWire))
        if bottom not in metals:
            raise ValueError(f"bottom is not a MetalWire of technology '{tech.name}'")
        if top not in metals:
            raise ValueError(f"top is not a MetalWire of technology '{tech.name}'")
        bottom_idx = metals.index(bottom)
        top_idx = metals.index(top)
        if bottom_idx >= top_idx:
            raise ValueError("bottom layer has to be below top layer")
        self.bottom = bottom
        self.top = top

        if not bottom_direction in self.directions:
            raise ValueError(f"bottom_direction has to be one of {self.directions}")
        self.bottom_direction = bottom_direction

        for wire, _ in pitches.items():
            if not (
                (wire in metals)
                and (bottom_idx <= metals.index(wire) <= top_idx)
            ):
                raise ValueError(f"wire '{wire.name}' is not part of the Gauge set")
        pitches2: Dict[prm.MetalWire, float] = {
            wire: _util.i2f(pitch) for wire, pitch in pitches.items()
        }
        self.pitches = pitches2

        for wire, _ in offsets.items():
            if not (
                (wire in metals)
                and (bottom_idx <= metals.index(wire) <= top_idx)
            ):
                raise ValueError(f"wire '{wire.name}' is not part of the Gauge set")
        offsets2: Dict[prm.MetalWire, float] = {
            wire: _util.i2f(offset) for wire, offset in offsets.items()
        }
        self.offsets = offsets2


class Library:
    def __init__(self, *,
        name: str, tech: tch.Technology, cktfab: Optional["ckt.CircuitFactory"]=None,
        layoutfab: Optional["lay.LayoutFactory"]=None,
        global_nets: OptSingleOrMulti[str].T=None,
    ):
        self.name = name
        self.tech = tech
        if cktfab is None:
            cktfab = ckt.CircuitFactory(tech)
        self.cktfab = cktfab
        if layoutfab is None:
            layoutfab = lay.LayoutFactory(tech)
        self.layoutfab = layoutfab

        if global_nets is not None:
            global_nets2 = cast(Tuple[str, ...], _util.v2t(global_nets))
            if not all(isinstance(net, str) for net in global_nets2):
                raise TypeError(
                    "global_nets has to be None, a string or an iterable of strings"
                )
            self.global_nets = frozenset(global_nets2)
        else:
            self.global_nets = None

        self.cells = _Cells()
    
    def new_cell(self, *, name: str):
        cell = _Cell(lib=self, name=name)
        self.cells += cell
        return cell

    @property
    def sorted_cells(self):
        cells = set()
        for cell in self.cells:
            if cell not in cells:
                for subcell in cell.subcells_sorted:
                    if subcell not in cells:
                        yield subcell
                        cells.add(subcell)
                yield cell
                cells.add(cell)


class StdCellLibrary(Library):
    def __init__(self, *,
        name: str, tech: tch.Technology, cktfab: Optional["ckt.CircuitFactory"]=None,
        layoutfab: Optional["lay.LayoutFactory"]=None,
        global_nets: OptSingleOrMulti[str].T=None,
        routinggauge: SingleOrMulti[RoutingGauge].T,
        pingrid_pitch: IntFloat, row_height: IntFloat,
    ):
        super().__init__(
            name=name, tech=tech, cktfab=cktfab, layoutfab=layoutfab,
            global_nets=global_nets,
        )

        self.routinggauge = _util.v2t(routinggauge)
        self.pingrid_pitch = _util.i2f(pingrid_pitch)
        self.row_height = _util.i2f(row_height)
