# SPDX-License-Identifier: GPL-2.0-or-later OR AGPL-3.0-or-later OR CERN-OHL-S-2.0+
# type: ignore
import unittest

from pdkmaster.technology import mask as _msk, net as _net, geometry as _geo
from pdkmaster.design import layout as _lay, library as _lbry

from ..dummy import dummy_tech, dummy_layoutfab, dummy_cktfab, dummy_lib
prims = dummy_tech.primitives


class TestNet(_net.Net):
    # Non-abstract net class
    def __init__(self, name: str):
        super().__init__(name)


class LayoutTest(unittest.TestCase):
    def test_maskshapessublayout(self):
        m1 = _msk.DesignMask(name="mask1", fill_space="no")
        m2 = _msk.DesignMask(name="mask2", fill_space="no")
        n1 = TestNet("net1")
        p = _geo.Point(x=3.0, y=-2.0)
        rot = _geo.Rotation.R90
        r1 = _geo.Rect(left=-3.0, bottom=-1.0, right=-1.0, top=1.0)
        r2 = _geo.Rect(left=1.0, bottom=-1.0, right=3.0, top=1.0)
        ms1 = _geo.MaskShape(mask=m1, shape=r1)
        ms2 = _geo.MaskShape(mask=m2, shape=r2)
        mssl1 = _lay.MaskShapesSubLayout(
            net=n1, shapes=_geo.MaskShapes(ms1),
        )
        mssl2 = _lay.MaskShapesSubLayout(
            net=None, shapes=_geo.MaskShapes(ms1),
        )
        mssl3 = _lay.MaskShapesSubLayout(
            net=n1, shapes=_geo.MaskShapes((ms1, ms2)),
        )
        mssl4 = mssl1.dup()
        mssl4.add_shape(shape=ms2)

        self.assertNotEqual(mssl1, "")
        self.assertNotEqual(mssl1, mssl2)
        with self.assertRaises(TypeError):
            hash(mssl1)
        self.assertNotEqual(mssl1, mssl4)
        self.assertEqual(mssl3, mssl4)
        # Get coverage for _hier_strs_, don't check output
        s = "\n".join(mssl1._hier_strs_)

        mssl5 = mssl3.moved(dxy=p)
        mssl4.move(dxy=p)

        self.assertNotEqual(mssl3, mssl5)
        self.assertEqual(mssl4, mssl5)

        mssl6 = mssl3.rotated(rotation=rot).moved(dxy=p)
        mssl7 = mssl3.dup()
        mssl7.rotate(rotation=rot)
        mssl7.move(dxy=p)

        self.assertEqual(mssl6, mssl7)

    def test_sublayouts(self):
        mask = prims.metal.mask

        r1 = _geo.Rect.from_floats(values=(0.0, 0.0, 1.0, 1.0))
        r2 = _geo.Rect.from_floats(values=(1.0, 0.0, 2.0, 1.0))

        ms1 = _geo.MaskShapes(_geo.MaskShape(mask=mask, shape=r1))
        ms2 = _geo.MaskShapes(_geo.MaskShape(mask=mask, shape=r2))

        sl1 = _lay.MaskShapesSubLayout(net=None, shapes=ms1)
        sl2 = _lay.MaskShapesSubLayout(net=None, shapes=ms2)

        with self.assertRaises(ValueError):
            _lay.SubLayouts((sl1, sl2))


class CircuitLayouterTest(unittest.TestCase):
    def test_addwire(self):
        # MetalWire
        wire = prims.metal

        ckt = dummy_cktfab.new_circuit(name="test")
        net = ckt.new_net(name="net", external=False)

        shape = _geo.Rect(left=1.0, bottom=-1.0, right=2.0, top=1.0)

        layouter = dummy_layoutfab.new_circuitlayouter(circuit=ckt, boundary=None)
        layouter.add_wire(net=net, wire=wire, shape=shape)

        layout = dummy_layoutfab.new_layout()
        layout.add_shape(net=net, prim=wire, shape=shape)

        self.assertEqual(layouter.layout, layout)

        # Via
        wire = prims.contact
        bottom = prims.poly

        ckt = dummy_cktfab.new_circuit(name="test")
        net = ckt.new_net(name="net", external=False)

        p = _geo.Point(x=-2.0, y=3.0)

        layouter = dummy_layoutfab.new_circuitlayouter(circuit=ckt, boundary=None)
        layouter.add_wire(net=net, wire=wire, origin=p, bottom=bottom)

        layout = dummy_layoutfab.new_layout()
        layout.add_primitive(portnets={"conn": net}, prim=wire, x=p.x, y=p.y, bottom=bottom)

        self.assertEqual(layouter.layout, layout)
