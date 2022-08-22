# SPDX-License-Identifier: GPL-2.0-or-later OR AGPL-3.0-or-later OR CERN-OHL-S-2.0+
# type: ignore
import unittest

from pdkmaster.technology import geometry as _geo
from pdkmaster.design import circuit as _ckt, layout as _lay

from ..dummy import dummy_layoutfab, dummy_lib

class CellTest(unittest.TestCase):
    def test_instsublayout(self):
        cell = dummy_lib.new_cell(name="test")
        cell.new_circuit()
        bb = _geo.Rect(left=0.0, bottom=0.0, right=1.0, top=2.0)
        cell.add_layout(layout=dummy_layoutfab.new_layout(boundary=bb))

        rot = _geo.Rotation.R90
        inst = _ckt._CellInstance(name="inst", cell=cell)
        sublay = _lay._InstanceSubLayout(
            inst=inst, origin=_geo.origin, layoutname=None, rotation=rot,
        )
        self.assertEqual(sublay.boundary, rot*bb)

        cell2 = dummy_lib.new_cell(name="test2")
        ckt = cell2.new_circuit()
        inst = ckt.instantiate(cell, name="inst")
        layouter = cell2.new_circuitlayouter()
        
        instlay = layouter.inst_layout(inst=inst, rotation=rot)
        self.assertEqual(instlay.boundary, rot*bb)

