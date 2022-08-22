# SPDX-License-Identifier: GPL-2.0-or-later OR AGPL-3.0-or-later OR CERN-OHL-S-2.0+
from typing import cast

from pdkmaster.typing import GDSLayerSpecDict
from pdkmaster.technology import (
    property_ as _prp, geometry as _geo, net as _net, primitive as _prm, technology_ as _tch
)
from pdkmaster.design import circuit as _ckt, layout as _lay,  library as _lbry


class MyNet(_net.Net):
    def __init__(self, *, name:str):
        super().__init__(name=name)


class EmptyTech(_tch.Technology):
    @property
    def name(self) -> str:
        return "Empty"
    @property
    def grid(self) -> float:
        return 0.005
    @property
    def substrate_type(self) -> str:
        return "n"

    def _init(self):
        pass
empty_tech = EmptyTech()


class DummyTech(_tch.Technology):
    @property
    def name(self) -> str:
        return "Dummy"
    @property
    def grid(self) -> float:
        return 0.005
    @property
    def substrate_type(self) -> str:
        return "n"
    
    def _init(self):
        prims = self.primitives

        nwell = _prm.Well(type_="n", name="nwell", min_width=1.5, min_space=1.5)
        nplus = _prm.Implant(type_="n", name="nplus", min_width=1.0, min_space=1.0)
        pplus = _prm.Implant(type_="p", name="pplus", min_width=1.0, min_space=1.0)
        active = _prm.WaferWire(
            name="active", min_width=0.3, min_space=0.2,
            allow_in_substrate=True, implant=(nplus, pplus), min_implant_enclosure=_prp.Enclosure(0.2),
            implant_abut="none", allow_contactless_implant=False,
            well=nwell, min_well_enclosure=_prp.Enclosure(1.0),
            min_substrate_enclosure=_prp.Enclosure(1.0),
            allow_well_crossing=False,
        )
        poly = _prm.GateWire(name="poly", min_width=0.25, min_space=0.25)
        prims += (nwell, nplus, pplus, active, poly)

        metalpin = _prm.Marker(name="metalpin")
        metal = _prm.TopMetalWire(name="metal", min_width=0.1, min_space=0.1, pin=metalpin)
        contact = _prm.Via(
            name="contact", width=0.35, min_space=0.35, bottom=(active, poly), top=metal,
            min_bottom_enclosure=_prp.Enclosure(0.2), min_top_enclosure=_prp.Enclosure(0.15),
        )
        prims += (contact, metalpin, metal)

        actres = _prm.Marker(name="actres")
        resistor = _prm.Resistor(
            name="resistor", wire=active, contact=None,
            indicator=actres, min_indicator_extension=0.4,
            model="resistor", model_params={"width": "w", "height": "l"},
        )
        prims += (actres, resistor)

        diodemark = _prm.Marker(name="diodemark")
        ndiode = _prm.Diode(
            name="ndiode", wire=active,
            indicator=diodemark, min_indicator_enclosure=_prp.Enclosure(0.2),
            implant=nplus, min_implant_enclosure=_prp.Enclosure(0.2),
            model="ndiode",
        )
        pdiode = _prm.Diode(
            name="pdiode", wire=active,
            indicator=diodemark, min_indicator_enclosure=_prp.Enclosure(0.2),
            implant=pplus, min_implant_enclosure=_prp.Enclosure(0.2),
            well=nwell, model="pdiode", 
        )
        prims += (diodemark, ndiode, pdiode)

        mosgate = _prm.MOSFETGate(
            name="mosgate", active=active, min_sd_width=0.35,
            poly=poly, min_polyactive_extension=0.45,
            contact=contact, min_contactgate_space=0.15,
        )
        nmos = _prm.MOSFET(
            name="nmos", gate=mosgate,
            implant=nplus, min_gateimplant_enclosure=_prp.Enclosure(0.25),
        )
        pmos = _prm.MOSFET(
            name="pmos", gate=mosgate,
            implant=pplus, min_gateimplant_enclosure=_prp.Enclosure(0.25),
            well=nwell,
        )
        prims +=  (mosgate, nmos, pmos)
dummy_tech = DummyTech()
dummy_cktfab = _ckt.CircuitFactory(tech=dummy_tech)
dummy_layoutfab = _lay.LayoutFactory(tech=dummy_tech)

dummy_gdslayers: GDSLayerSpecDict = {
    mask.name: (i + 1) if i%2 == 0 else (i + 1, 1)
    for i, mask in enumerate(dummy_tech.designmasks)
}


dummy_lib = _lbry.Library(name="dummy_lib", tech=dummy_tech)
def _lib_init():
    # The dummy_lib will be initialized with different shapes to maximize
    # code coverage when being used for example in export code etc.
    prims = dummy_tech.primitives
    metal = cast(_prm.TopMetalWire, prims.metal)

    rect1 = _geo.Rect(left=0.0, bottom=0.0, right=1.0, top=1.0)
    rect2 = _geo.Rect(left=1.0, bottom=0.0, right=2.0, top=1.0)
    rect12 = _geo.Rect(left=0.0, bottom=0.0, right=2.0, top=1.0)
    lshape = _geo.Polygon.from_floats(points=(
        (0.0, 0.0), (0.0, 3.0), (1.0, 3.0), (1.0, 1.0), (2.0, 1.0), (2.0, 0.0), (0.0, 0.0),
    ))

    # cell1: rect shape
    cell1 = dummy_lib.new_cell(name="cell1")
    ckt = cell1.new_circuit()
    layouter = cell1.new_circuitlayouter()
    layout = layouter.layout

    i = ckt.new_net(name="i", external=True)
    layouter.add_wire(net=i, wire=metal, pin=prims.metalpin, shape=rect1)
    layouter.layout.boundary = rect1

    # cell2: cell instance
    cell2 = dummy_lib.new_cell(name="cell2")
    ckt = cell2.new_circuit()
    layouter = cell2.new_circuitlayouter()

    inst = ckt.instantiate(cell1, name="inst")
    layouter.place(object_=inst, origin=_geo.origin)
    layouter.layout.boundary = rect1

    # cell3: polygon
    cell3 = dummy_lib.new_cell(name="cell3")
    ckt = cell3.new_circuit()
    layouter = cell3.new_circuitlayouter()

    i = ckt.new_net(name="i", external=True)
    layouter.add_wire(net=i, wire=metal, pin=prims.metalpin, shape=lshape)
    layouter.layout.boundary = lshape.bounds

    # cell4: multipartshape
    cell4 = dummy_lib.new_cell(name="cell4")
    ckt = cell4.new_circuit()
    layouter = cell4.new_circuitlayouter()

    mps = _geo.MultiPartShape(fullshape=rect12, parts=(rect1, rect2))
    
    i1 = ckt.new_net(name="i1", external=False)
    i2 = ckt.new_net(name="i2", external=False)

    layout.add_shape(prim=metal, net=i1, shape=mps.parts[0])
    layout.add_shape(prim=metal, net=i2, shape=mps.parts[1])
_lib_init()
